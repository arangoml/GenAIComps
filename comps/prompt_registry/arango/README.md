# 🧾 Prompt Registry Microservice with MongoDB

This README provides setup guides and all the necessary information about the Prompt Registry microservice with ArangoDB database.

---

## Setup Environment Variables

```bash
export http_proxy=${your_http_proxy} 
export https_proxy=${your_http_proxy}
export ARANGODB_PORT=${ARANGODB_PORT} 
export OPEA_DB_NAME=${OPEA_DB_NAME}
export COLLECTION_NAME=${COLLECTION_NAME}
```

---

## 🚀Start Microservice with Docker

### Build Docker Image

```bash
cd ~/GenAIComps
docker build -t opea/prompt_registry-arango-server:latest -f comps/prompt_registry/arango/DockerFile .
```

### Run Docker with CLI

- Run Aranago DB and prompt_registry-arango conatiner using the following command
```bash
docker-compose -f comps/prompt_registry/arango/docker-compose-prompt-registry-arango.yaml up
```

---

### ✅ Invoke Microservice

NOTE: please replace ${host_ip} with IP address of the host machine running prompt registry service
The Prompt Registry microservice exposes the following API endpoints:

- Save prompt

  ```bash
  curl -X 'POST' \
    http://${host_ip}:6018/v1/prompt/create \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{
      "prompt_text": "test prompt", "user": "test"
  }'
  ```

- Retrieve prompt from database by user

  ```bash
  curl -X 'POST' \
    http://${host_ip}:6018/v1/prompt/get \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{
    "user": "test"}'
  ```

- Retrieve prompt from database by prompt_id

  ```bash
  curl -X 'POST' \
    http://${host_ip}:6018/v1/prompt/get \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{
    "user": "test", "prompt_id":"{_id returned from save prompt route above}"}'
  ```

- Retrieve relevant prompt by keyword

  ```bash
  curl -X 'POST' \
    http://${host_ip}:6018/v1/prompt/get \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{
    "user": "test", "prompt_text": "{keyword to search}"}'
  ```

- Delete prompt by prompt_id

  ```bash
  curl -X 'POST' \
    http://${host_ip}:6018/v1/prompt/delete \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{
    "user": "test", "prompt_id":"{prompt_id to be deleted}"}'
  ```
