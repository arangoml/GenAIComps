# Copyright (C) 2024 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import os
import time
from typing import Any, Optional, Union

from arango import ArangoClient
from config import (
    ARANGO_DB_NAME,
    ARANGO_DISTANCE_STRATEGY,
    ARANGO_EMBEDDING_DIMENSION,
    ARANGO_EMBEDDING_FIELD,
    ARANGO_GRAPH_NAME,
    ARANGO_NUM_CENTROIDS,
    ARANGO_PASSWORD,
    ARANGO_TEXT_FIELD,
    ARANGO_TRAVERSAL_ENABLED,
    ARANGO_TRAVERSAL_MAX_DEPTH,
    ARANGO_URL,
    ARANGO_USE_APPROX_SEARCH,
    ARANGO_USERNAME,
    HUGGINGFACEHUB_API_TOKEN,
    OPENAI_API_KEY,
    OPENAI_EMBED_MODEL,
    TEI_EMBED_MODEL,
    TEI_EMBEDDING_ENDPOINT,
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

# TODO: Revisit these classes. How would they be presented in ChatQnA?
# class ArangoTextDoc(TextDoc):
#     neighborhood: Optional[list[dict[str, Any]]] = None

# class ArangoRetrievalResponseData(RetrievalResponseData):
#     neighborhood: Optional[list[dict[str, Any]]] = None


logger = CustomLogger("retriever_arango")
logflag = os.getenv("LOGFLAG", False)


def fetch_neighborhoods(
    vector_db: ArangoVector,
    keys: list[str],
    neighborhoods: dict[str, Any],
    graph_name: str,
    source_collection_name: str,
    max_depth: int,
) -> None:
    """Fetch neighborhoods of source documents. Updates the neighborhoods dictionary in-place."""
    if max_depth < 1:
        max_depth = 1

    # TODO: Consider using general `GRAPH` syntax instead of specific edge collections...
    aql = f"""
        FOR doc IN @@collection
            FILTER doc._key IN @keys

            LET entity_neighborhood = (
                FOR v1, e1, p1 IN 1..1 INBOUND doc {graph_name}_HAS_SOURCE
                    FOR v2, e2, p2 IN 1..{max_depth} ANY v1 {graph_name}_LINKS_TO
                        RETURN p2
            )

            RETURN {{[doc._key]: entity_neighborhood}}
    """

    bind_vars = {
        "@collection": source_collection_name,
        "keys": keys,
    }

    cursor = vector_db.db.aql.execute(aql, bind_vars=bind_vars)

    for doc in cursor:
        neighborhoods.update(doc)

    if logflag:
        logger.info(f"Fetched neighborhoods for {len(neighborhoods)} documents.")


@register_microservice(
    name="opea_service@retriever_arango",
    service_type=ServiceType.RETRIEVER,
    endpoint="/v1/retrieval",
    host="0.0.0.0",
    port=7000,
)
@register_statistics(names=["opea_service@retriever_arango"])
async def retrieve(
    input: Union[EmbedDoc, RetrievalRequest, ChatCompletionRequest]
) -> Union[SearchedDoc, RetrievalResponse, ChatCompletionRequest]:
    if logflag:
        logger.info(input)

    if isinstance(input, EmbedDoc):
        empty_result = SearchedDoc(retrieved_docs=[], initial_query=input.text)
    elif isinstance(input, RetrievalRequest):
        empty_result = RetrievalResponse(retrieved_docs=[])
    elif isinstance(input, ChatCompletionRequest):
        input.retrieved_docs = []
        input.documents = []
        empty_result = input
    else:
        raise ValueError("Invalid input type: ", type(input))

    start = time.time()

    query = input.text if isinstance(input, EmbedDoc) else input.input
    embedding = input.embedding if isinstance(input.embedding, list) else None

    ########################
    # Fetch the Graph Name #
    ########################

    # This is a workaround as the ChatQnA UI is limited to
    # a single input field, so we need to parse the graph name from the query (for now).

    graph_name = None
    query_split = query.split("|")

    if len(query) == 2:
        # e.g "Who is connected to John Smith? | PersonGraph"
        query = query_split[0].strip()
        graph_name = query_split[1].strip()

    if not graph_name:
        graph_name = ARANGO_GRAPH_NAME

    source_collection_name = f"{graph_name}_SOURCE"

    if not db.has_graph(graph_name):
        if logflag:
            logger.error(f"Graph '{graph_name}' does not exist in ArangoDB.")

        return empty_result

    if not db.has_collection(source_collection_name):
        if logflag:
            logger.error(f"Collection '{source_collection_name}' does not exist in ArangoDB.")

        return empty_result

    collection_count = db.collection(source_collection_name).count()
    if collection_count == 0:
        if logflag:
            logger.error(f"Collection '{source_collection_name}' is empty.")

        return empty_result

    if collection_count < ARANGO_NUM_CENTROIDS:
        if logflag:
            m = f"Collection '{source_collection_name}' has fewer documents ({collection_count}) than the number of centroids ({ARANGO_NUM_CENTROIDS})."
            logger.error(m)

        return empty_result

    ######################
    # Compute Similarity #
    ######################

    vector_db = ArangoVector(
        embedding=embeddings,
        embedding_dimension=ARANGO_EMBEDDING_DIMENSION,
        database=db,
        collection_name=source_collection_name,
        embedding_field=ARANGO_EMBEDDING_FIELD,
        text_field=ARANGO_TEXT_FIELD,
        distance_strategy=ARANGO_DISTANCE_STRATEGY,
        num_centroids=ARANGO_NUM_CENTROIDS,
    )

    try:
        if input.search_type == "similarity_score_threshold":
            docs_and_similarities = await vector_db.asimilarity_search_with_relevance_scores(
                query=query,
                embedding=embedding,
                k=input.k,
                score_threshold=input.score_threshold,
                use_approx=ARANGO_USE_APPROX_SEARCH,
            )
            search_res = [doc for doc, _ in docs_and_similarities]
        elif input.search_type == "mmr":
            search_res = await vector_db.amax_marginal_relevance_search(
                query=query,
                embedding=embedding,
                k=input.k,
                fetch_k=input.fetch_k,
                lambda_mult=input.lambda_mult,
                use_approx=ARANGO_USE_APPROX_SEARCH,
            )
        else:
            # Default to basic similarity search
            search_res = await vector_db.asimilarity_search(
                query=query,
                embedding=embedding,
                k=input.k,
                use_approx=ARANGO_USE_APPROX_SEARCH,
            )
    except Exception as e:
        if logflag:
            logger.error(f"Error during similarity search: {e}")

        return empty_result

    if not search_res:
        if logflag:
            logger.info("No documents found.")

        return empty_result

    ########################################
    # Traverse Source Documents (optional) #
    ########################################

    neighborhoods = {}
    if ARANGO_TRAVERSAL_ENABLED:
        fetch_neighborhoods(
            vector_db,
            neighborhoods,
            [r.id for r in search_res],
            graph_name,
            ARANGO_TRAVERSAL_MAX_DEPTH,
        )

    ####################
    # Process Response #
    ####################

    search_res_tuples = []
    for r in search_res:
        page_content = r.page_content
        neighborhood = neighborhoods.get(r.id)

        text = page_content
        if neighborhood:
            text += f"\n--------\nDocument Neighborhood:\n{neighborhood}"

        search_res_tuples.append((r.id, text, r.metadata))

    retrieved_docs: Union[list[TextDoc], list[RetrievalResponseData]] = []
    if isinstance(input, EmbedDoc):
        retrieved_docs = [TextDoc(id=id, text=text) for id, text, _ in search_res_tuples]
        result = SearchedDoc(retrieved_docs=retrieved_docs, initial_query=input.text)

    else:
        retrieved_docs = [
            RetrievalResponseData(id=id, text=text, metadata=metadata) for id, text, metadata in search_res_tuples
        ]

        if isinstance(input, RetrievalRequest):
            result = RetrievalResponse(retrieved_docs=retrieved_docs)

        else:
            input.retrieved_docs = retrieved_docs
            input.documents = [doc.text for doc in retrieved_docs]
            result = input

    statistics_dict["opea_service@retriever_arango"].append_latency(time.time() - start, None)

    if logflag:
        logger.info(result)

    return result


if __name__ == "__main__":

    if not ARANGO_EMBEDDING_DIMENSION:
        raise ValueError("EMBED_DIMENSION must specified in advance.")

    if OPENAI_API_KEY and OPENAI_EMBED_MODEL:
        # Use OpenAI embeddings
        embeddings = OpenAIEmbeddings(model=OPENAI_EMBED_MODEL, dimensions=ARANGO_EMBEDDING_DIMENSION)
    elif TEI_EMBEDDING_ENDPOINT and HUGGINGFACEHUB_API_TOKEN:
        # create embeddings using TEI endpoint service
        embeddings = HuggingFaceHubEmbeddings(
            model=TEI_EMBEDDING_ENDPOINT, huggingfacehub_api_token=HUGGINGFACEHUB_API_TOKEN
        )
    else:
        # create embeddings using local embedding model
        embeddings = HuggingFaceBgeEmbeddings(model_name=TEI_EMBED_MODEL)

    client = ArangoClient(hosts=ARANGO_URL)
    sys_db = client.db(name="_system", username=ARANGO_USERNAME, password=ARANGO_PASSWORD, verify=True)

    if not sys_db.has_database(ARANGO_DB_NAME):
        sys_db.create_database(ARANGO_DB_NAME)

    db = client.db(name=ARANGO_DB_NAME, username=ARANGO_USERNAME, password=ARANGO_PASSWORD, verify=True)
    if logflag:
        logger.info(f"Connected to ArangoDB {db.version()}.")

    opea_microservices["opea_service@retriever_arango"].start()
