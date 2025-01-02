# Retriever Microservice with ArangoDB

## 🚀 1. Start Microservice with Python

### Install Requirements

```bash
pip install -r requirements.txt
apt-get install libtesseract-dev -y
apt-get install poppler-utils -y
```

### Start ArangoDB Server

To launch ArangoDB locally, first ensure you have docker installed. Then, you can launch the database with the following docker command.

```bash
docker run -d --name arangodb -p 8529:8529 -e ARANGO_ROOT_PASSWORD=password arangodb/arangodb:latest
```

### Setup Environment Variables

```bash
export no_proxy=${your_no_proxy}
export http_proxy=${your_http_proxy}
export https_proxy=${your_http_proxy}
export ARANGO_URL=${your_arango_url}
export ARANGO_USERNAME=${your_arango_username}
export ARANGO_PASSWORD=${your_arango_password}
export ARANGO_DB_NAME=${your_db_name}
export ARANGO_COLLECTION_NAME=${your_collection_name}
export ARANGO_EMBEDDING_DIMENSION=${your_embedding_dimension}
export PYTHONPATH=${path_to_comps}
```

See below for additional environment variables that can be set.

### Start Retriever Service

```bash
python retriever_arangodb.py
```

## 🚀 2. Start Microservice with Docker

### Build Docker Image

```bash
cd /your/path/to/GenAIComps
docker build -t opea/retriever-arango:latest --build-arg https_proxy=$https_proxy --build-arg http_proxy=$http_proxy -f comps/retrievers/arangodb/langchain/Dockerfile .
```

### Run Docker with CLI

```bash
docker run -d --name="retriever-arango-server" -p 7000:7000 --ipc=host -e http_proxy=$http_proxy -e https_proxy=$https_proxy -e ...  opea/retriever-arango:latest
```

### Run Docker with Docker Compose

```bash
cd /your/path/to/GenAIComps/comps/retriever/arango/langchain
docker compose -f docker-compose-retriever-arango.yaml up -d
```

## 🚀 3. Consume Retriever Service

### 3.1 Check Service Status

```bash
curl http://${your_ip}:7000/v1/health_check \
  -X GET \
  -H 'Content-Type: application/json'
```

### 3.2 Consume Embedding Service

Assuming you have an ArangoDB Collection with the documents you want to retrieve from, you can consume the retriever service with the following curl command. 

```bash
curl http://${your_ip}:7000/v1/retrieval \
  -X POST \
  -d "{\"text\":\"What is the revenue of Nike in 2023?\",\"embedding\":[]}" \
  -H 'Content-Type: application/json'
```

If `embedding` is not specified or is an empty list, the retriever will use the text to generate an embedding using the Embedding Environment variables provided.

Additional parameters can be set for the retriever:

```bash
curl http://localhost:7000/v1/retrieval \
  -X POST \
  -d "{\"text\":\"What is the revenue of Nike in 2023?\",\"embedding\":[],\"search_type\":\"similarity\", \"k\":4}" \
  -H 'Content-Type: application/json'
```

```bash
curl http://localhost:7000/v1/retrieval \
  -X POST \
  -d "{\"text\":\"What is the revenue of Nike in 2023?\",\"embedding\":[],\"search_type\":\"similarity_score_threshold\", \"k\":4, \"score_threshold\":0.2}" \
  -H 'Content-Type: application/json'
```

```bash
export your_embedding=$(python -c "import random; embedding = [random.uniform(-1, 1) for _ in range(768)]; print(embedding)")
curl http://localhost:7000/v1/retrieval \
  -X POST \
  -d "{\"text\":\"What is the revenue of Nike in 2023?\",\"embedding\":[],\"search_type\":\"mmr\", \"k\":4, \"fetch_k\":20, \"lambda_mult\":0.5}" \
  -H 'Content-Type: application/json'
```

---

Additional options that can be specified from the environment variables are as follows (default values are also in the `config.py` file):

ArangoDB Connection configuration
- `ARANGO_URL`: The URL for the ArangoDB service.
- `ARANGO_USERNAME`: The username for the ArangoDB service.
- `ARANGO_PASSWORD`: The password for the ArangoDB service.
- `ARANGO_DB_NAME`: The name of the database to use for the ArangoDB service.

ArangoDB Collection configuration
- `ARANGO_COLLECTION_NAME`: The name of the collection containing the documents.
- `ARANGO_DISTANCE_STRATEGY`: The distance strategy to use for the embeddings. Options are `COSINE` and `L2` (euclidean distance).
- `ARANGO_USE_APPROX_SEARCH`: Whether to use approximate neighbor search. If False, exact search will be used (slower, but more accurate). If True, approximate search will be used (faster, but less accurate). Defaults to `True`.
- `ARANGO_TEXT_FIELD`:  The document field name storing the text.
- `ARANGO_EMBEDDING_FIELD`: The document field name storing the embeddings.
- `ARANGO_EMBEDDING_DIMENSION`: The dimension of the document embeddings.
- `ARANGO_NUM_CENTROIDS`: The number of centroids to use for the approximate search. Defaults to `1`, which is essentially exhaustive search.

ArangoDB Traversal configuration
- `ARANGO_TRAVERSAL_GRAPH_NAME`: If specified, the retriever will traverse the graph to retrieve the neighborhood of the retrieved documents.
- `ARANGO_TRAVERSAL_MAX_DEPTH`: The maximum depth to traverse the graph. Defaults to `1`.

Embedding Configuration
- `TEI_EMBED_MODEL`: The model to use for the TEI service. Defaults to `BAAI/bge-base-en-v1.5`.
- `TEI_EMBEDDING_ENDPOINT`: The endpoint for the TEI service.
- `HUGGINGFACEHUB_API_TOKEN`: The API token for the Hugging Face Hub.

OpenAI Configuration:
**Note**: This configuration can replace the TGI and TEI services for text generation and embeddings.
- `OPENAI_API_KEY`: The API key for the OpenAI service.
- `OPENAI_EMBED_MODEL`: The embedding model to use for the OpenAI service. Defaults to `text-embedding-3-small`.