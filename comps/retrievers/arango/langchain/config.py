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
ARANGO_USE_APPROX_SEARCH = os.getenv("ARANGO_USE_APPROX_SEARCH", "false").lower() == "true"
ARANGO_TEXT_FIELD = os.getenv("ARANGO_TEXT_FIELD", "text")
ARANGO_EMBEDDING_FIELD = os.getenv("ARANGO_EMBEDDING_FIELD", "embedding")
ARANGO_NUM_CENTROIDS = os.getenv("ARANGO_NUM_CENTROIDS", 1)

# ArangoDB Traversal configuration
ARANGO_TRAVERSAL_ENABLED = os.getenv("ARANGO_TRAVERSAL_ENABLED", "false").lower() == "true"
ARANGO_TRAVERSAL_MAX_DEPTH = os.getenv("ARANGO_TRAVERSAL_MAX_DEPTH", 0)
ARANGO_TRAVERSAL_MAX_RETURNED = os.getenv("ARANGO_TRAVERSAL_MAX_RETURNED", 0)

# Summarizer Configuration
SUMMARIZER_ENABLED = os.getenv("SUMMARIZER_ENABLED", "false").lower() == "true"

# Text Embeddings Inference configuration
TEI_EMBEDDING_ENDPOINT = os.getenv("TEI_EMBEDDING_ENDPOINT")
HUGGINGFACEHUB_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")
TEI_EMBED_MODEL = os.getenv("TEI_EMBED_MODEL", "BAAI/bge-base-en-v1.5")

# VLLM configuration
VLLM_ENDPOINT = os.getenv("VLLM_ENDPOINT")
VLLM_MODEL_ID = os.getenv("VLLM_MODEL_ID", "Intel/neural-chat-7b-v3-3")
VLLM_MAX_NEW_TOKENS = os.getenv("VLLM_MAX_NEW_TOKENS", 512)
VLLM_TOP_P = os.getenv("VLLM_TOP_P", 0.9)
VLLM_TEMPERATURE = os.getenv("VLLM_TEMPERATURE", 0.8)
VLLM_TIMEOUT = os.getenv("VLLM_TIMEOUT", 600)

# OpenAI configuration (alternative to VLLM & TEI)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o")
OPENAI_CHAT_TEMPERATURE = os.getenv("OPENAI_CHAT_TEMPERATURE", 0)
OPENAI_EMBED_MODEL = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")
OPENAI_CHAT_ENABLED = os.getenv("OPENAI_CHAT_ENABLED", "true").lower() == "true"
OPENAI_EMBED_ENABLED = os.getenv("OPENAI_EMBED_ENABLED", "true").lower() == "true"
