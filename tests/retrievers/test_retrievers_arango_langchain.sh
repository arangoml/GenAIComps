#!/bin/bash
# Copyright (C) 2024 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

set -x

WORKPATH=$(dirname "$PWD")
LOG_PATH="$WORKPATH/tests"
ip_address=$(hostname -I | awk '{print $1}')

export ARANGO_URL=${ARANGO_URL:-"http://${ip_address}:8529"} 
export ARANGO_USERNAME=${ARANGO_USERNAME:-"root"}
export ARANGO_PASSWORD=${ARANGO_PASSWORD:-"test"}
export ARANGO_DB_NAME=${ARANGO_DB_NAME:-"_system"}
export ARANGO_COLLECTION_NAME=${ARANGO_COLLECTION_NAME:-"test"}
export ARANGO_EMBEDDING_DIMENSION=${ARANGO_EMBEDDING_DIMENSION:-5}

function build_docker_images() {
    cd $WORKPATH
    echo $(pwd)
    docker run -d -p 8529:8529 --name=test-comps-arango -e ARANGO_ROOT_PASSWORD=$ARANGO_PASSWORD arangodb/arangodb:latest
    sleep 1m

    # Create ARANGO_COLLECTION_NAME
    curl -X POST --header 'accept: application/json' \
    --header 'Content-Type: application/json' \
    --data '{"name": "'${ARANGO_COLLECTION_NAME}'", "type": 2, "waitForSync": true}' \
    "${ARANGO_URL}/_db/${ARANGO_DB_NAME}/_api/collection" \
    -u ${ARANGO_USERNAME}:${ARANGO_PASSWORD}

    # Insert data into arango: {text: "test", embedding: [0.1, 0.2, 0.3, 0.4, 0.5]}
    curl -X POST --header 'accept: application/json' \
    --header 'Content-Type: application/json' \
    --data '{"text": "test", "embedding": [0.1, 0.2, 0.3, 0.4, 0.5]}' \
    "${ARANGO_URL}/_db/${ARANGO_DB_NAME}/_api/document/${ARANGO_COLLECTION_NAME}" \
    -u ${ARANGO_USERNAME}:${ARANGO_PASSWORD}

    docker build --no-cache -t opea/retriever-arango:comps --build-arg https_proxy=$https_proxy --build-arg http_proxy=$http_proxy -f comps/retrievers/arango/langchain/Dockerfile .
    if [ $? -ne 0 ]; then
        echo "opea/retriever-arango built fail"
        exit 1
    else
        echo "opea/retriever-arango built successful"
    fi
}

function start_service() {
    # tei endpoint
    tei_endpoint=5434
    model="BAAI/bge-base-en-v1.5"
    docker run -d --name="test-comps-retriever-arango-tei-endpoint" -p $tei_endpoint:80 -v ./data:/data --pull always ghcr.io/huggingface/text-embeddings-inference:cpu-1.5 --model-id $model
    sleep 30s
    export TEI_EMBEDDING_ENDPOINT="http://${ip_address}:${tei_endpoint}"

    # unset http_proxy
    export no_proxy="localhost,127.0.0.1,"${ip_address}
    docker run -d --name="test-comps-retriever-arango-server" \
    -p 7000:7000 \
    --ipc=host \
    -e http_proxy=$http_proxy \
    -e https_proxy=$https_proxy \
    -e ARANGO_URL=$ARANGO_URL \
    -e ARANGO_USERNAME=$ARANGO_USERNAME \
    -e ARANGO_PASSWORD=$ARANGO_PASSWORD \
    -e ARANGO_DB_NAME=$ARANGO_DB_NAME \
    -e ARANGO_COLLECTION_NAME=$ARANGO_COLLECTION_NAME \
    -e ARANGO_EMBEDDING_DIMENSION=$ARANGO_EMBEDDING_DIMENSION \
    -e TEI_EMBEDDING_ENDPOINT=$TEI_EMBEDDING_ENDPOINT \
    opea/retriever-arango:comps

    sleep 1m
}

function validate_microservice() {
    export PATH="${HOME}/miniforge3/bin:$PATH"
    source activate
    URL="http://${ip_address}:7000/v1/retrieval"

    test_embedding="[0.1, 0.2, 0.3, 0.4, 0.5]"
    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X POST -d "{\"text\":\"test\",\"embedding\":${test_embedding}}" -H 'Content-Type: application/json' "$URL")
    if [ "$HTTP_STATUS" -eq 200 ]; then
        echo "[ retriever ] HTTP status is 200. Checking content..."
        local CONTENT=$(curl -s -X POST -d "{\"text\":\"test\",\"embedding\":${test_embedding}}" -H 'Content-Type: application/json' "$URL" | tee ${LOG_PATH}/retriever.log)

        if echo "$CONTENT" | grep -q "retrieved_docs"; then
            echo "[ retriever ] Content is as expected."
        else
            echo "[ retriever ] Content does not match the expected result: $CONTENT"
            docker logs test-comps-retriever-arango-server >> ${LOG_PATH}/retriever.log
            docker logs test-comps-retriever-arango-tei-endpoint >> ${LOG_PATH}/tei.log
            exit 1
        fi
    else
        echo "[ retriever ] HTTP status is not 200. Received status was $HTTP_STATUS"
        docker logs test-comps-retriever-arango-server >> ${LOG_PATH}/retriever.log
        docker logs test-comps-retriever-arango-tei-endpoint >> ${LOG_PATH}/tei.log
        exit 1
    fi
}

function stop_docker() {
    cid_retrievers=$(docker ps -aq --filter "name=test-comps-retriever-arango*")
    if [[ ! -z "$cid_retrievers" ]]; then
        docker stop $cid_retrievers && docker rm $cid_retrievers && sleep 1s
    fi
    cid_db=$(docker ps -aq --filter "name=test-comps-arango-apoc1")
    if [[ ! -z "$cid_retrievers" ]]; then
        docker stop $cid_retrievers && docker rm $cid_retrievers && sleep 1s
    fi
}

function main() {

    stop_docker

    build_docker_images
    start_service

    validate_microservice

    stop_docker
    echo y | docker system prune

}

main
