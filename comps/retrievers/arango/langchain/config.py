# Copyright (C) 2024 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import os

# ArangoDB Connection configuration
ARANGO_URL = os.getenv("ARANGO_URL", "http://localhost:8529")
ARANGO_USERNAME = os.getenv("ARANGO_USERNAME", "root")
ARANGO_PASSWORD = os.getenv("ARANGO_PASSWORD", "test")
ARANGO_DB_NAME = os.getenv("ARANGO_DB_NAME", "_system")

# ArangoDB Vector configuration
ARANGO_GRAPH_NAME = os.getenv("ARANGO_GRAPH_NAME", "GRAPH")
ARANGO_DISTANCE_STRATEGY = os.getenv("ARANGO_DISTANCE_STRATEGY", "COSINE")
ARANGO_USE_APPROX_SEARCH = os.getenv("ARANGO_USE_APPROX_SEARCH", "true").lower() == "true"
ARANGO_TEXT_FIELD = os.getenv("ARANGO_TEXT_FIELD", "text")
ARANGO_EMBEDDING_FIELD = os.getenv("ARANGO_EMBEDDING_FIELD", "embedding")
ARANGO_NUM_CENTROIDS = int(os.getenv("ARANGO_NUM_CENTROIDS", 1))

# ArangoDB Traversal configuration
ARANGO_TRAVERSAL_ENABLED = os.getenv("ARANGO_TRAVERSAL_ENABLED", "false").lower() == "true"
ARANGO_TRAVERSAL_MAX_DEPTH = int(os.getenv("ARANGO_TRAVERSAL_MAX_DEPTH", 1))

# Embedding configuration
TEI_EMBED_MODEL = os.getenv("TEI_EMBED_MODEL", "BAAI/bge-base-en-v1.5")
TEI_EMBEDDING_ENDPOINT = os.getenv("TEI_EMBEDDING_ENDPOINT", "")
HUGGINGFACEHUB_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")

# OpenAI configuration (alternative to TEI & local model)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_EMBED_MODEL = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")
