﻿# Copyright (C) 2024 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
import os
from typing import Optional

from fastapi import HTTPException
from arango_store import DocumentStore
from pydantic import BaseModel

from comps import CustomLogger
from comps.cores.mega.micro_service import opea_microservices, register_microservice
from comps.cores.proto.api_protocol import ChatCompletionRequest

logger = CustomLogger("chathistory_arango")
logflag = os.getenv("LOGFLAG", False)


class ChatMessage(BaseModel):
    data: ChatCompletionRequest
    first_query: Optional[str] = None
    id: Optional[str] = None


class ChatId(BaseModel):
    user: str
    id: Optional[str] = None


def get_first_string(value):
    if isinstance(value, str):
        return value
    elif isinstance(value, list):
        # Assuming we want the first string from the first dictionary
        if value and isinstance(value[0], dict):
            first_dict = value[0]
            if first_dict:
                # Get the first value from the dictionary
                first_key = next(iter(first_dict))
                return first_dict[first_key]


@register_microservice(
    name="opea_service@chathistory_arango",
    endpoint="/v1/chathistory/create",
    host="0.0.0.0",
    input_datatype=ChatMessage,
    port=6012,
)
def create_documents(document: ChatMessage):
    """Creates or updates a document in the document store.

    Args:
        document (ChatMessage): The ChatMessage object containing the data to be stored.

    Returns:
        The result of the operation if successful, None otherwise.
    """
    if logflag:
        logger.info(document)
    try:
        if document.data.user is None:
            raise HTTPException(status_code=500, detail="Please provide the user information")
        store = DocumentStore(document.data.user)
        store.initialize_storage()
        if document.first_query is None:
            document.first_query = get_first_string(document.data.messages)
        if document.id:
            res = store.update_document(document.id, document.data, document.first_query)
        else:
            res = store.save_document(document)
        if logflag:
            logger.info(res)
        return res
    except Exception as e:
        logger.info(f"An error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@register_microservice(
    name="opea_service@chathistory_arango",
    endpoint="/v1/chathistory/get",
    host="0.0.0.0",
    input_datatype=ChatId,
    port=6012,
)
def get_documents(document: ChatId):
    """Retrieves documents from the document store based on the provided ChatId.

    Args:
        document (ChatId): The ChatId object containing the user and optional document id.

    Returns:
        The retrieved documents if successful, None otherwise.
    """
    if logflag:
        logger.info(document)
    try:
        store = DocumentStore(document.user)
        store.initialize_storage()
        if document.id is None:
            res = store.get_all_documents_of_user()
        else:
            res = store.get_user_documents_by_id(document.id)
        if logflag:
            logger.info(res)
        return res
    except Exception as e:
        # Handle the exception here
        logger.info(f"An error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@register_microservice(
    name="opea_service@chathistory_arango",
    endpoint="/v1/chathistory/delete",
    host="0.0.0.0",
    input_datatype=ChatId,
    port=6012,
)
def delete_documents(document: ChatId):
    """Deletes a document from the document store based on the provided ChatId.

    Args:
        document (ChatId): The ChatId object containing the user and document id.

    Returns:
        The result of the deletion if successful, None otherwise.
    """
    if logflag:
        logger.info(document)
    try:
        store = DocumentStore(document.user)
        store.initialize_storage()
        if document.id is None:
            raise Exception("Document id is required.")
        else:
            res = store.delete_document(document.id)
        if logflag:
            logger.info(res)
        return res
    except Exception as e:
        # Handle the exception here
        logger.info(f"An error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    #opea_microservices["opea_service@chathistory_arango"].start()
    print("Creating document")
    doc_id = create_documents(ChatMessage(data=ChatCompletionRequest(user="test", messages="test Messages"), first_query=None))
    breakpoint()
    doc_id_2 = create_documents(ChatMessage(data=ChatCompletionRequest(user="test", messages="test Messages 2"), first_query=None))
    breakpoint()
    # test get document by id
    print(f"Getting document with id: {doc_id_2}")
    print(get_documents(ChatId(user="test", id=doc_id_2)))
    # # test get all documents
    print(f"Getting all documents for user: test")
    breakpoint()
    print(get_documents(ChatId(user="test", id=None)))
    # test update document
    create_documents(ChatMessage(data=ChatCompletionRequest(user="test", messages="test Messages 3"), first_query=None, id=doc_id_2))
    breakpoint()
    print(f"Getting document with id: {doc_id_2}")
    print(get_documents(ChatId(user="test", id=doc_id_2)))
    # test delete document
    breakpoint()
    delete_documents(ChatId(user="test", id=doc_id_2))
    print(f"Deleted document with id: {doc_id_2}")
