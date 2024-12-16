# Copyright (C) 2024 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import os

# ArangoDB configuration
ARANGO_URL = os.getenv("ARANGO_URL", "http://localhost:8529")
ARANGO_USERNAME = os.getenv("ARANGO_USERNAME", "root")
ARANGO_PASSWORD = os.getenv("ARANGO_PASSWORD", "test")
ARANGO_DB_NAME = os.getenv("ARANGO_DB_NAME", "_system")
ARANGO_COLLECTION_NAME = os.getenv("ARANGO_COLLECTION_NAME", "SOURCE")
ARANGO_DISTANCE_STRATEGY = os.getenv("ARANGO_DISTANCE_STRATEGY", "COSINE")
ARANGO_TEXT_FIELD = os.getenv("ARANGO_TEXT_FIELD", "text")
ARANGO_EMBBEDDING_FIELD = os.getenv("ARANGO_EMBEDDING_FIELD", "metadata.embedding")
ARANGO_PERFORM_NEIGHBOURHOOD_SAMPLING = os.getenv("ARANGO_PERFORM_NEIGHBOURHOOD_SAMPLING", False)
ARANGO_EMBED_DIMENSION = os.getenv("ARANGO_EMBED_DIMENSION")
ARANGO_NUM_CENTROIDS = os.getenv("ARANGO_NUM_CENTROIDS", 1)

# Embedding configuration
EMBED_MODEL = os.getenv("EMBED_MODEL", "BAAI/bge-base-en-v1.5")
EMBED_ENDPOINT = os.getenv("TEI_EMBEDDING_ENDPOINT", "")
HUGGINGFACEHUB_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")

# OpenAI configuration (alternative to TEI & local model)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_EMBED_MODEL = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")
