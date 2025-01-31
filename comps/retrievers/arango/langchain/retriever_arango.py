# Copyright (C) 2024 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import os
import time
from typing import Any, Union

import openai
from arango import ArangoClient
from config import (
    ARANGO_DB_NAME,
    ARANGO_DISTANCE_STRATEGY,
    ARANGO_EMBEDDING_FIELD,
    ARANGO_GRAPH_NAME,
    ARANGO_NUM_CENTROIDS,
    ARANGO_PASSWORD,
    ARANGO_TEXT_FIELD,
    ARANGO_TRAVERSAL_ENABLED,
    ARANGO_TRAVERSAL_MAX_DEPTH,
    ARANGO_TRAVERSAL_MAX_RETURNED,
    ARANGO_URL,
    ARANGO_USE_APPROX_SEARCH,
    ARANGO_USERNAME,
    HUGGINGFACEHUB_API_TOKEN,
    OPENAI_API_KEY,
    OPENAI_CHAT_ENABLED,
    OPENAI_CHAT_MODEL,
    OPENAI_CHAT_TEMPERATURE,
    OPENAI_EMBED_MODEL,
    SUMMARIZER_ENABLED,
    TEI_EMBED_MODEL,
    TEI_EMBEDDING_ENDPOINT,
    TGI_LLM_ENDPOINT,
    TGI_LLM_MAX_NEW_TOKENS,
    TGI_LLM_TEMPERATURE,
    TGI_LLM_TIMEOUT,
    TGI_LLM_TOP_K,
    TGI_LLM_TOP_P,
)
from langchain_community.embeddings import HuggingFaceBgeEmbeddings, HuggingFaceHubEmbeddings
from langchain_community.vectorstores.arangodb_vector import ArangoVector
from langchain_huggingface import HuggingFaceEndpoint
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

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

logger = CustomLogger("retriever_arango")
logflag = os.getenv("LOGFLAG", True)


class HuggingFaceEndpointPatch(HuggingFaceEndpoint):
    def _call(
        self,
        prompt,
        stop=None,
        run_manager=None,
        **kwargs,
    ) -> str:
        """Call out to HuggingFace Hub's inference endpoint."""
        import json

        invocation_params = self._invocation_params(stop, **kwargs)
        if self.streaming:
            completion = ""
            for chunk in self._stream(prompt, stop, run_manager, **invocation_params):
                completion += chunk.text
            return completion
        else:
            invocation_params["stop"] = invocation_params[
                "stop_sequences"
            ]  # porting 'stop_sequences' into the 'stop' argument
            response = self.client.post(
                json={"inputs": prompt, "parameters": invocation_params},
                stream=False,
                task=self.task,
                # NOTE: This is the only change from the original method
                # So far I have yet to find a way to use the original class.
                # In this case, self.model is set to TGI_LLM_ENDPOINT:
                model=self.model,
            )
            response_text = json.loads(response.decode())[0]["generated_text"]

            # Maybe the generation has stopped at one of the stop sequences:
            # then we remove this stop sequence from the end of the generated text
            for stop_seq in invocation_params["stop_sequences"]:
                if response_text[-len(stop_seq) :] == stop_seq:
                    response_text = response_text[: -len(stop_seq)]
            return response_text


def fetch_neighborhoods(
    vector_db: ArangoVector,
    keys: list[str],
    graph_name: str,
    source_collection_name: str,
) -> dict[str, Any]:
    """Fetch neighborhoods of source documents"""

    if ARANGO_TRAVERSAL_MAX_DEPTH <= 0:
        start_vertex = "v1"
        links_to_query = ""
    else:
        start_vertex = "v2"
        links_to_query = (
            f"FOR v2 IN 1..{ARANGO_TRAVERSAL_MAX_DEPTH} ANY v1 {graph_name}_LINKS_TO OPTIONS {{uniqueEdges: 'path'}}"
        )

    if ARANGO_TRAVERSAL_MAX_RETURNED <= 0:
        limit_query = ""
    else:
        # TODO: Revisit strategy for limiting returned neighborhoods
        limit_query = f"""
            LET score = COSINE_SIMILARITY(doc.{ARANGO_EMBEDDING_FIELD}, s.{ARANGO_EMBEDDING_FIELD})
            SORT score DESC
            LIMIT {ARANGO_TRAVERSAL_MAX_RETURNED}
        """

    aql = f"""
        FOR doc IN @@collection
            FILTER doc._key IN @keys

            LET source_neighborhood = (
                FOR v1 IN 1..1 INBOUND doc {graph_name}_HAS_SOURCE
                    {links_to_query}
                        FOR s IN 1..1 OUTBOUND {start_vertex} {graph_name}_HAS_SOURCE
                            FILTER s._key != doc._key
                            {limit_query}
                            COLLECT id = s._key, text = s.{ARANGO_TEXT_FIELD}
                            RETURN {{[id]: text}}
            )

            RETURN {{[doc._key]: source_neighborhood}}
    """

    bind_vars = {
        "@collection": source_collection_name,
        "keys": keys,
    }

    cursor = vector_db.db.aql.execute(aql, bind_vars=bind_vars)

    neighborhoods = {}
    for doc in cursor:
        neighborhoods.update(doc)

    return neighborhoods


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

    if len(query_split) == 2:
        # e.g "Who is connected to John Smith? | PersonGraph"
        query = query_split[0].strip()
        graph_name = query_split[1].strip()

    if not graph_name:
        graph_name = ARANGO_GRAPH_NAME

    source_collection_name = f"{graph_name}_SOURCE"

    if not db.has_graph(graph_name):
        if logflag:
            graph_names = [g["name"] for g in db.graphs()]
            logger.error(f"Graph '{graph_name}' does not exist in ArangoDB. Graphs: {graph_names}")

        return empty_result

    if not db.graph(graph_name).has_vertex_collection(source_collection_name):
        if logflag:
            collection_names = db.graph(graph_name).vertex_collections()
            m = f"Collection '{source_collection_name}' does not exist in graph '{graph_name}'. Collections: {collection_names}"
            logger.error(m)

        return empty_result

    collection = db.collection(source_collection_name)

    collection_count = collection.count()
    if collection_count == 0:
        if logflag:
            logger.error(f"Collection '{source_collection_name}' is empty.")

        return empty_result

    if collection_count < ARANGO_NUM_CENTROIDS:
        if logflag:
            m = f"Collection '{source_collection_name}' has fewer documents ({collection_count}) than the number of centroids ({ARANGO_NUM_CENTROIDS})."
            logger.error(m)

        return empty_result

    ################################
    # Retrieve Embedding Dimension #
    ################################

    random_doc = collection.random()
    random_doc_id = random_doc["_id"]

    embedding = random_doc.get(ARANGO_EMBEDDING_FIELD)

    if not embedding:
        if logflag:
            logger.error(f"Document '{random_doc_id}' is missing field '{ARANGO_EMBEDDING_FIELD}'.")

        return empty_result

    if not isinstance(embedding, list):
        if logflag:
            logger.error(f"Document '{random_doc_id}' has a non-list embedding field, found {type(embedding)}.")

        return empty_result

    dimension = len(embedding)

    if dimension == 0:
        if logflag:
            logger.error(f"Document '{random_doc_id}' has an empty embedding field.")

        return empty_result

    if OPENAI_API_KEY and OPENAI_EMBED_MODEL:
        # Use OpenAI embeddings
        embeddings = OpenAIEmbeddings(model=OPENAI_EMBED_MODEL, dimensions=dimension)
    elif TEI_EMBEDDING_ENDPOINT and HUGGINGFACEHUB_API_TOKEN:
        # create embeddings using TEI endpoint service
        embeddings = HuggingFaceHubEmbeddings(
            model=TEI_EMBEDDING_ENDPOINT, huggingfacehub_api_token=HUGGINGFACEHUB_API_TOKEN
        )
    else:
        # create embeddings using local embedding model
        embeddings = HuggingFaceBgeEmbeddings(model_name=TEI_EMBED_MODEL)

    ######################
    # Compute Similarity #
    ######################

    if logflag:
        logger.info(f"Searching for similar documents...")

    vector_db = ArangoVector(
        embedding=embeddings,
        embedding_dimension=dimension,
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

    if logflag:
        logger.info(f"Found {len(search_res)} documents.")

    ########################################
    # Traverse Source Documents (optional) #
    ########################################

    if ARANGO_TRAVERSAL_ENABLED:
        neighborhoods = fetch_neighborhoods(
            vector_db=vector_db,
            keys=[r.id for r in search_res],
            graph_name=graph_name,
            source_collection_name=source_collection_name,
        )

        for r in search_res:
            neighborhood = neighborhoods.get(r.id)

            if neighborhood:
                r.page_content += "\n------\nRELATED CHUNKS:\n------\n"
                r.page_content += str(neighborhood)

        if logflag:
            logger.info(f"Added neighborhoods to {len(search_res)} documents.")

    ################################
    # Summarize Results (optional) #
    ################################

    if SUMMARIZER_ENABLED:
        # TODO: Revisit the quality of this template and parameterize it.
        def generate_prompt(query: str, text: str) -> str:
            return f"""
                I've performed vector similarity on the following
                query to retrieve most relevant documents: '{query}' 

                Each retrieved Document may have a 'RELATED CHUNKS' section.

                Please consider summarizing the Document below using the query as the foundation to summarize the text.

                The Document: {text}

                Provide a summary to include all content relevant to the query, using the RELATED CHUNKS section (if provided) as needed.

                Your summary:
            """

        for r in search_res:
            prompt = generate_prompt(query, r.page_content)

            res = llm.invoke(prompt)
            summarized_text = res.content
            tokens_used = res.usage_metadata

            if logflag:
                logger.info(f"Summarized {r.id} (used {tokens_used} tokens)")

            r.page_content = summarized_text

    ####################
    # Process Response #
    ####################

    search_res_tuples = [(r.id, r.page_content, r.metadata) for r in search_res]

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

    ########################################
    # Text Generation Inference (optional) #
    ########################################

    if OPENAI_API_KEY and OPENAI_CHAT_ENABLED:
        if logflag:
            logger.info("OpenAI API Key is set. Verifying its validity...")
        openai.api_key = OPENAI_API_KEY

        try:
            openai.models.list()

            if logflag:
                logger.info("OpenAI API Key is valid.")

            llm = ChatOpenAI(temperature=OPENAI_CHAT_TEMPERATURE, max_tokens=512, model_name=OPENAI_CHAT_MODEL)
        except openai.error.AuthenticationError:
            if logflag:
                logger.info("OpenAI API Key is invalid.")
        except Exception as e:
            if logflag:
                logger.info(f"An error occurred while verifying the API Key: {e}")

    elif TGI_LLM_ENDPOINT:
        llm = HuggingFaceEndpointPatch(
            endpoint_url=TGI_LLM_ENDPOINT,
            max_new_tokens=TGI_LLM_MAX_NEW_TOKENS,
            top_k=TGI_LLM_TOP_K,
            top_p=TGI_LLM_TOP_P,
            temperature=TGI_LLM_TEMPERATURE,
            timeout=TGI_LLM_TIMEOUT,
        )
    else:
        raise ValueError("No text generation environment variables are set, cannot generate graphs.")

    ############
    # ArangoDB #
    ############

    client = ArangoClient(hosts=ARANGO_URL)
    sys_db = client.db(name="_system", username=ARANGO_USERNAME, password=ARANGO_PASSWORD, verify=True)

    if not sys_db.has_database(ARANGO_DB_NAME):
        sys_db.create_database(ARANGO_DB_NAME)

    db = client.db(name=ARANGO_DB_NAME, username=ARANGO_USERNAME, password=ARANGO_PASSWORD, verify=True)
    if logflag:
        logger.info(f"Connected to ArangoDB {db.version()}.")

    opea_microservices["opea_service@retriever_arango"].start()
