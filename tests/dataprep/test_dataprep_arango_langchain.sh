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

function build_docker_images() {
    cd $WORKPATH
    echo $(pwd)
    docker run -d -p 8529:8529 --name=test-comps-arango -e ARANGO_ROOT_PASSWORD=$ARANGO_PASSWORD arangodb/arangodb:latest
    sleep 1m

    docker build --no-cache -t opea/dataprep-arango:comps --build-arg https_proxy=$https_proxy --build-arg http_proxy=$http_proxy -f $WORKPATH/comps/dataprep/arango/langchain/Dockerfile .
    if [ $? -ne 0 ]; then
        echo "opea/dataprep-arango built fail"
        exit 1
    else
        echo "opea/dataprep-arango built successful"
    fi
}

function start_service() {
    tgi_endpoint=5044
    # Remember to set HF_TOKEN before invoking this test!
    export HUGGINGFACEHUB_API_TOKEN=${HF_TOKEN}
    model=Intel/neural-chat-7b-v3-3
    docker run -d --name="test-comps-dataprep-tgi-endpoint" -p $tgi_endpoint:80 -v ./data:/data --shm-size 1g ghcr.io/huggingface/text-generation-inference:1.4 --model-id $model
    export TGI_LLM_ENDPOINT="http://${ip_address}:${tgi_endpoint}"

    # unset http_proxy
    export no_proxy="localhost,127.0.0.1,"${ip_address}
    docker run -d --name="test-comps-dataprep-arango-server" \
    -p 6007:6007 \
    --ipc=host \
    -e http_proxy=$http_proxy \
    -e https_proxy=$https_proxy \
    -e ARANGO_URL=$ARANGO_URL \
    -e ARANGO_USERNAME=$ARANGO_USERNAME \
    -e ARANGO_PASSWORD=$ARANGO_PASSWORD \
    -e ARANGO_DB_NAME=$ARANGO_DB_NAME \
    -e TGI_LLM_ENDPOINT=$TGI_LLM_ENDPOINT \
    opea/dataprep-arango:comps

    sleep 1m
}


function validate_microservice() {
    cd $LOG_PATH

    # test /v1/dataprep
    URL="http://${ip_address}:6007/v1/dataprep"
    echo "Deep learning is a subset of machine learning that utilizes neural networks with multiple layers to analyze various levels of abstract data representations. It enables computers to identify patterns and make decisions with minimal human intervention by learning from large amounts of data." > $LOG_PATH/dataprep_file.txt
    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X POST -F 'files=@./dataprep_file.txt' -H 'Content-Type: multipart/form-data' "$URL")
    if [ "$HTTP_STATUS" -eq 200 ]; then
        echo "[ dataprep ] HTTP status is 200. Checking content..."
        cp ./dataprep_file.txt ./dataprep_file2.txt
        local CONTENT=$(curl -s -X POST -F 'files=@./dataprep_file2.txt' -H 'Content-Type: multipart/form-data' "$URL" | tee ${LOG_PATH}/dataprep.log)

        if echo "$CONTENT" | grep -q "Data preparation succeeded"; then
            echo "[ dataprep ] Content is as expected."
        else
            echo "[ dataprep ] Content does not match the expected result: $CONTENT"
            docker logs test-comps-dataprep-arango >> ${LOG_PATH}/dataprep.log
            exit 1
        fi
    else
        echo "[ dataprep ] HTTP status is not 200. Received status was $HTTP_STATUS"
        docker logs test-comps-dataprep-arango >> ${LOG_PATH}/dataprep.log
        exit 1
    fi
}

function stop_docker() {
    cid=$(docker ps -aq --filter "name=test-comps-arango*")
    if [[ ! -z "$cid" ]]; then docker stop $cid && docker rm $cid && sleep 1s; fi

    cid=$(docker ps -aq --filter "name=test-comps-dataprep-arango*")
    if [[ ! -z "$cid" ]]; then docker stop $cid && docker rm $cid && sleep 1s; fi
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
