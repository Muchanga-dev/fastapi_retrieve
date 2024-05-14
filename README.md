# fastapi_retrieve

O `fastapi_retrieve` é um sistema de recuperação de informações baseado em texto que permite aos usuários fazer perguntas e receber respostas de documentos indexados. A aplicação utiliza o FastAPI no backend para lidar com a indexação e recuperação de texto de documentos PDF, enquanto o frontend é desenvolvido em Streamlit, permitindo uma interação fácil e rápida com a API.

## Estrutura do Projeto

Este projeto está organizado da seguinte maneira:

- **backend/**:
  - `api.py`: Implementação do servidor FastAPI que lida com a extração e indexação de texto, além de responder a consultas.
- **data/**:
  - **input/**:
    - `dados_estruturado.pdf`: Documento PDF de onde o texto é extraído.
  - **output/**:
    - `{base_name}_index.index`: Arquivo de índice Faiss para buscas rápidas.
    - `{base_name}_embeddings.npy`: Vetores de embeddings.
    - `{base_name}_texts.npy`: Textos extraídos.
- **frontend/**:
  - `app.py`: Aplicativo frontend construído com Streamlit que permite aos usuários fazer perguntas e receber respostas.

## Pré-requisitos

- Python 3.10 ou superior

## Instalação

**Clonar o repositório**:
  ```
   git clone https://github.com/Muchanga-dev/fastapi_retrieve.git
   cd fastapi_retrieve
   ```
- Instalar dependências (recomenda-se usar um ambiente virtual):

**Copiar código**

```pip install -r requirements.txt```

- Execução
Iniciar o servidor backend:

**Copiar código:**

```uvicorn backend.api:app --reload --port 8000```

- Iniciar o aplicativo frontend (em um novo terminal):

**Copiar código:**

```streamlit run frontend/app.py```

Agora, acesse http://localhost:8501 no seu navegador para interagir com o frontend do Streamlit.

Usando a API
Você pode fazer perguntas diretamente através da interface do Streamlit, que está configurada para enviar perguntas ao backend e exibir as respostas.

Contribuição
Contribuições são bem-vindas! Por favor, faça um fork do repositório, faça suas mudanças e submeta um pull request para revisão.

Licença
Distribuído sob a licença MIT. Veja LICENSE para mais informações.
