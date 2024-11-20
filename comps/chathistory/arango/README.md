# 📝 Chat History Microservice with ArangoDB

This README provides setup guides and all the necessary information about the Chat History microservice with ArangoDB database.

---

## Setup Environment Variables

```bash
export http_proxy=${your_http_proxy}
export https_proxy=${your_http_proxy}
export MONGO_HOST=${MONGO_HOST}
export MONGO_PORT=27017
export DB_NAME=${DB_NAME}
export COLLECTION_NAME=${COLLECTION_NAME}
```

```bash
export ARANGODB_HOST=${ARANGODB_HOST}
export ARANGODB_PORT=${ARANGODB_PORT}
export ARANGODB_USERNAME=${ARANGODB_USERNAME}
export ARANGODB_PASSWORD=${ARANGODB_PASSWORD}
export DB_NAME=${DB_NAME}
export COLLECTION_NAME=${COLLECTION_NAME}
export PYTHONPATH={Path to base of directory}
```

---

## 🚀Start Microservice with Docker

### Create Docker Network

```bash
docker network create chathistory-network
``` 

### Build Docker Image

```bash
cd ../../../../
docker build -t opea/chathistory-arango-server:latest --build-arg https_proxy=$https_proxy --build-arg http_proxy=$http_proxy -f comps/chathistory/arango/Dockerfile .
```

### Run Docker with CLI

- Run ArangoDB image container

  ```bash
  docker run -d -p 8529:8529 --network=chathistory-network --name=arango arangodb/arangodb:latest

  docker start arango
  ```

- Run the Chat History microservice

  ```bash
  docker run -p 6012:6012 \  --network chathistory-network \    
  -e http_proxy=$http_proxy \
  -e https_proxy=$https_proxy \
  -e no_proxy=$no_proxy \
  -e ARANGODB_HOST=host.docker.internal \
  -e ARANGODB_PORT=${ARANGODB_PORT} \
  -e DB_NAME=${DB_NAME} \
  -e COLLECTION_NAME=${COLLECTION_NAME} \
  -e ARANGODB_USERNAME=${ARANGODB_USERNAME} \
  -e ARANGODB_PASSWORD=${ARANGODB_PASSWORD} \
  opea/chathistory-arango-server:latest

  ```

---

## ✅ Invoke Microservice

The Chat History microservice exposes the following API endpoints:

- Create new chat conversation

  ```bash
  curl -X 'POST' \
    http://${host_ip}:6012/v1/chathistory/create \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{
    "data": {
      "messages": "test Messages", "user": "test"
    }
  }'
  ```

- Get all the Conversations for a user

  ```bash
  curl -X 'POST' \
    http://${host_ip}:6012/v1/chathistory/get \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{
    "user": "test"}'
  ```

- Get a specific conversation by id.

  ```bash
  curl -X 'POST' \
    http://localhost:6012/v1/chathistory/get \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{
    "user": "test", "id":"673255bad3e51a6fdef12b5e"}'
  ```

- Update the conversation by id.

  ```bash
  curl -X 'POST' \
    http://localhost:6012/v1/chathistory/create \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{
    "data": {
      "messages": "test Messages Update", "user": "test"
    },
    "id":"673255bad3e51a6fdef12b5e"
  }'
  ```

- Delete a stored conversation.

  ```bash
  curl -X 'POST' \
    http://${host_ip}:6012/v1/chathistory/delete \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{
    "user": "test", "id":"668620173180b591e1e0cd74"}'
  ```
