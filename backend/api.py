# -*- coding: utf-8 -*-
"""
Created on Sat May 11 12:53:19 2024

@author: mucha 'data/input/protocolo.pdf'
"""
import os
import re
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pdfplumber
import uvicorn
import logging

# Configuração básica de logging
logging.basicConfig(level=logging.INFO)

# Caminho direto para o documento específico
pdf_path = 'data/input/dados_estruturado.pdf'  # Atualize para o caminho específico do seu PDF
output_dir = 'data/output'

# Nome base do documento para indexação
base_name = os.path.splitext(os.path.basename(pdf_path))[0]
index_path = os.path.join(output_dir, f"{base_name}_index.index")
embedding_path = os.path.join(output_dir, f"{base_name}_embeddings.npy")
texts_path = os.path.join(output_dir, f"{base_name}_texts.npy")

# Inicializar o modelo globalmente com um modelo avançado
model = SentenceTransformer('sentence-transformers/multi-qa-MiniLM-L6-cos-v1')

# Função para segmentar texto em perguntas e respostas e indexar
def extrair_e_indexar_texto(pdf_path, index_path, embedding_path, texts_path):
    logging.info(f"Verificando existência do índice para: {pdf_path}")

    if os.path.exists(index_path) and os.path.exists(embedding_path) and os.path.exists(texts_path):
        logging.info(f"Índice e embeddings já existem para {pdf_path}, pulando criação.")
        return

    logging.info(f"Extraindo texto do PDF: {pdf_path}")
    questions_answers = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            full_text = ""
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n"

        # Segmentar o texto em perguntas e respostas
        questions_answers = segmentar_texto(full_text)

        # Extrair respostas e criar embeddings
        entries = [format_section(qa) for qa in questions_answers]
        titles = [entry['title'] for entry in entries]
        embeddings = model.encode(titles, show_progress_bar=True)

        # Criar e salvar o índice
        index = faiss.IndexFlatL2(embeddings.shape[1])
        index.add(np.array(embeddings))

        faiss.write_index(index, index_path)
        np.save(embedding_path, embeddings)
        np.save(texts_path, np.array(entries, dtype=object))

        logging.info(f"Index, embeddings e textos salvos em {output_dir}")
    except Exception as e:
        logging.error(f"Erro ao processar o PDF {pdf_path}: {e}")
        raise

def segmentar_texto(text):
    # Remove quebras de linha múltiplas e excessivas
    text = re.sub(r'\n{2,}', '\n', text)

    # Regex para identificar títulos de perguntas
    question_pattern = r'^\d+\.\s.*'

    questions_answers = []
    current_question = None
    lines = text.split('\n')

    for line in lines:
        line = line.strip()
        if re.match(question_pattern, line):
            if current_question:
                questions_answers.append(current_question)
            current_question = {'title': line, 'answer': ""}
        else:
            if current_question and line:
                current_question['answer'] += line + " "

    if current_question:
        questions_answers.append(current_question)

    return questions_answers

def format_section(qa):
    return {'title': qa['title'], 'text': qa['answer'].strip()}

# Extrair, segmentar e criar índice para `doc.pdf`
extrair_e_indexar_texto(pdf_path, index_path, embedding_path, texts_path)

# Inicializar FastAPI
app = FastAPI()

class QueryModel(BaseModel):
    question: str

@app.post("/ask")
def ask_question(query: QueryModel):
    try:
        question = query.question
        logging.info(f"Recebendo pergunta: {question} para o documento: {pdf_path}")

        # Verificar existência de arquivos de índice
        if not os.path.exists(index_path) or not os.path.exists(embedding_path) or not os.path.exists(texts_path):
            logging.error(f"Índice, embeddings ou textos não encontrados para {pdf_path}")
            raise HTTPException(status_code=404, detail="Índice, embeddings ou textos não encontrados")

        # Carregar índice e textos segmentados
        logging.info(f"Carregando índice de {index_path}")
        index = faiss.read_index(index_path)
        logging.info(f"Carregando textos segmentados de {texts_path}")
        questions_answers = np.load(texts_path, allow_pickle=True).tolist()

        # Gerar embedding para pergunta
        logging.info(f"Gerando embedding para a pergunta: {question}")
        question_embedding = model.encode([question], convert_to_tensor=False)

        # Executar busca no índice com similaridade coseno e normalização L2
        logging.info("Executando busca no índice")
        D, I = index.search(np.array(question_embedding), k=100)
        best_distance = D[0][0]

        # Verificar se há resultado válido (distância menor que infinito)
        if best_distance < float('inf'):
            # Selecionar o resultado mais próximo (menor distância)
            best_idx = np.argmin(D[0])
            best_context = questions_answers[I[0][best_idx]]
        else:
            raise HTTPException(status_code=404, detail="Não foram encontrados resultados relevantes para a sua pergunta.")

        # Estruturar a resposta
        response = {
            "question": question,
            "context": best_context
        }

        logging.info(f"Resposta gerada: {response}")
        return response

    except HTTPException as http_exc:
        logging.error(f"Erro HTTP: {http_exc.detail}")
        raise http_exc

    except Exception as e:
        logging.error(f"Erro ao processar a pergunta: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

# Iniciar a aplicação Uvicorn
def start_uvicorn():
    uvicorn.run(app, host="0.0.0.0", port=8000)

# Checar se o script está sendo executado diretamente
if __name__ == "__main__":
    start_uvicorn()