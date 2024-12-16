# Copyright (C) 2024 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import os
import time
from typing import Union

from arango import ArangoClient
from config import (
    ARANGO_COLLECTION_NAME,
    ARANGO_DB_NAME,
    ARANGO_DISTANCE_STRATEGY,
    ARANGO_EMBBEDDING_FIELD,
    ARANGO_NUM_CENTROIDS,
    ARANGO_PASSWORD,
    ARANGO_PERFORM_NEIGHBOURHOOD_SAMPLING,
    ARANGO_TEXT_FIELD,
    ARANGO_URL,
    ARANGO_USERNAME,
    ARANGO_EMBED_DIMENSION,
    EMBED_ENDPOINT,
    EMBED_MODEL,
    HUGGINGFACEHUB_API_TOKEN,
    OPENAI_API_KEY,
    OPENAI_EMBED_MODEL,
)
from langchain_community.embeddings import HuggingFaceBgeEmbeddings, HuggingFaceHubEmbeddings
from langchain_community.vectorstores.arangodb_vector import ArangoVector
from langchain_openai import OpenAIEmbeddings

from comps import (
    CustomLogger,
    EmbedDoc,
    SearchedDoc,
    ServiceType,
    TextDoc,
    opea_microservices,
    register_microservice,
    register_statistics,
    statistics_dict,
)
from comps.cores.proto.api_protocol import (
    ChatCompletionRequest,
    RetrievalRequest,
    RetrievalResponse,
    RetrievalResponseData,
)

logger = CustomLogger("retriever_arangodb")
logflag = os.getenv("LOGFLAG", False)


@register_microservice(
    name="opea_service@retriever_arangodb",
    service_type=ServiceType.RETRIEVER,
    endpoint="/v1/retrieval",
    host="0.0.0.0",
    port=7000,
)
@register_statistics(names=["opea_service@retriever_arangodb"])
async def retrieve(
    input: Union[EmbedDoc, RetrievalRequest, ChatCompletionRequest]
) -> Union[SearchedDoc, RetrievalResponse, ChatCompletionRequest]:
    if logflag:
        logger.info(input)
    start = time.time()

    index = vector_db.retrieve_vector_index()
    if index is None and db.collection(vector_db.collection_name).count() > 0:
        vector_db.create_vector_index()

    query = input.text if isinstance(input, EmbedDoc) else input.input
    embedding = input.embedding if isinstance(input.embedding, list) else None
    k = input.k

    if input.search_type == "similarity":
        if not input.embedding:
            raise ValueError("Embedding must be provided for similarity retriever")

        search_res = await vector_db.asimilarity_search_by_vector(query=query, embedding=embedding, k=k)
    elif input.search_type == "similarity_distance_threshold":
        if input.distance_threshold is None:
            raise ValueError("distance_threshold must be provided for similarity_distance_threshold retriever")
        if not embedding:
            raise ValueError("Embedding must not be None for similarity_distance_threshold retriever")

        search_res = await vector_db.asimilarity_search_by_vector(
            query=query,
            embedding=embedding,
            k=k,
            distance_threshold=input.distance_threshold,
        )
    elif input.search_type == "similarity_score_threshold":
        docs_and_similarities = await vector_db.asimilarity_search_with_relevance_scores(
            query=query, embedding=embedding, k=k, score_threshold=input.score_threshold
        )
        search_res = [doc for doc, _ in docs_and_similarities]
    elif input.search_type == "mmr":
        search_res = await vector_db.amax_marginal_relevance_search(
            query=query, embedding=embedding, k=k, fetch_k=input.fetch_k, lambda_mult=input.lambda_mult
        )
    else:
        raise ValueError(f"Search Type '{input.search_type}' not valid")

    # return different response format
    retrieved_docs = []
    if isinstance(input, EmbedDoc):
        for r in search_res:
            retrieved_docs.append(TextDoc(text=r.page_content))
        result = SearchedDoc(retrieved_docs=retrieved_docs, initial_query=input.text)
    else:
        for r in search_res:
            retrieved_docs.append(RetrievalResponseData(text=r.page_content, metadata=r.metadata))
        if isinstance(input, RetrievalRequest):
            result = RetrievalResponse(retrieved_docs=retrieved_docs)
        elif isinstance(input, ChatCompletionRequest):
            input.retrieved_docs = retrieved_docs
            input.documents = [doc.text for doc in retrieved_docs]
            result = input

    if ARANGO_PERFORM_NEIGHBOURHOOD_SAMPLING:
        # TODO
        pass

    statistics_dict["opea_service@retriever_arangodb"].append_latency(time.time() - start, None)

    if logflag:
        logger.info(result)

    return result


if __name__ == "__main__":

    if not ARANGO_EMBED_DIMENSION:
        raise ValueError("EMBED_DIMENSION must specified in advance.")

    if OPENAI_API_KEY and OPENAI_EMBED_MODEL:
        # Use OpenAI embeddings
        embeddings = OpenAIEmbeddings(model=OPENAI_EMBED_MODEL, dimensions=ARANGO_EMBED_DIMENSION)

    elif EMBED_ENDPOINT and HUGGINGFACEHUB_API_TOKEN:
        # create embeddings using TEI endpoint service
        embeddings = HuggingFaceHubEmbeddings(model=EMBED_ENDPOINT, huggingfacehub_api_token=HUGGINGFACEHUB_API_TOKEN)
    else:
        # create embeddings using local embedding model
        embeddings = HuggingFaceBgeEmbeddings(model_name=EMBED_MODEL)

    client = ArangoClient(hosts=ARANGO_URL)
    sys_db = client.db(name="_system", username=ARANGO_USERNAME, password=ARANGO_PASSWORD, verify=True)

    if not sys_db.has_database(ARANGO_DB_NAME):
        sys_db.create_database(ARANGO_DB_NAME)

    db = client.db(name=ARANGO_DB_NAME, username=ARANGO_USERNAME, password=ARANGO_PASSWORD, verify=True)

    vector_db = ArangoVector(
        embedding=embeddings,
        embedding_dimension=ARANGO_EMBED_DIMENSION,
        database=db,
        collection_name=ARANGO_COLLECTION_NAME,
        embedding_field=ARANGO_EMBBEDDING_FIELD,
        text_field=ARANGO_TEXT_FIELD,
        distance_strategy=ARANGO_DISTANCE_STRATEGY,
        num_centroids=ARANGO_NUM_CENTROIDS,
    )

    opea_microservices["opea_service@retriever_arangodb"].start()
