# Copyright (C) 2024 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import os

# ArangoDB Connection configuration
ARANGO_URL = os.getenv("ARANGO_URL", "http://localhost:8529")
ARANGO_USERNAME = os.getenv("ARANGO_USERNAME", "root")
ARANGO_PASSWORD = os.getenv("ARANGO_PASSWORD", "test")
ARANGO_DB_NAME = os.getenv("ARANGO_DB_NAME", "_system")

# ArangoDB Graph Insertion configuration
ARANGO_INSERT_ASYNC = os.getenv("ARANGO_INSERT_ASYNC", "false").lower() == "true"
ARANGO_BATCH_SIZE = os.getenv("ARANGO_BATCH_SIZE", 500)
ARANGO_GRAPH_NAME = os.getenv("ARANGO_GRAPH_NAME", "GRAPH")
ARANGO_USE_GRAPH_NAME = os.getenv("ARANGO_USE_GRAPH_NAME", "true").lower() == "true"

# VLLM configuration
VLLM_ENDPOINT = os.getenv("VLLM_ENDPOINT")
VLLM_MODEL_ID = os.getenv("VLLM_MODEL_ID", "Intel/neural-chat-7b-v3-3")
VLLM_MAX_NEW_TOKENS = os.getenv("VLLM_MAX_NEW_TOKENS", 512)
VLLM_TOP_P = os.getenv("VLLM_TOP_P", 0.9)
VLLM_TEMPERATURE = os.getenv("VLLM_TEMPERATURE", 0.8)
VLLM_TIMEOUT = os.getenv("VLLM_TIMEOUT", 600)

# Text Embeddings Inference configuration
TEI_EMBEDDING_ENDPOINT = os.getenv("TEI_EMBEDDING_ENDPOINT")
HUGGINGFACEHUB_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")
TEI_EMBED_MODEL = os.getenv("TEI_EMBED_MODEL", "BAAI/bge-base-en-v1.5")
EMBED_SOURCE_DOCUMENTS = os.getenv("EMBED_SOURCE_DOCUMENTS", "true").lower() == "true"
EMBED_NODES = os.getenv("EMBED_NODES", "false").lower() == "true"
EMBED_RELATIONSHIPS = os.getenv("EMBED_RELATIONSHIPS", "false").lower() == "true"

# OpenAI configuration (alternative to VLLM & TEI)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o")
OPENAI_CHAT_TEMPERATURE = os.getenv("OPENAI_CHAT_TEMPERATURE", 0)
OPENAI_EMBED_MODEL = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")
OPENAI_EMBED_DIMENSION = os.getenv("OPENAI_EMBED_DIMENSION", 768)
OPENAI_CHAT_ENABLED = os.getenv("OPENAI_CHAT_ENABLED", "true").lower() == "true"
OPENAI_EMBED_ENABLED = os.getenv("OPENAI_EMBED_ENABLED", "true").lower() == "true"

# LLMGraphTransformer configuration
SYSTEM_PROMPT_PATH = os.getenv("SYSTEM_PROMPT_PATH")
ALLOWED_NODES = os.getenv("ALLOWED_NODES", [])
ALLOWED_RELATIONSHIPS = os.getenv("ALLOWED_RELATIONSHIPS", [])
NODE_PROPERTIES = os.getenv("NODE_PROPERTIES", ["description"])
RELATIONSHIP_PROPERTIES = os.getenv("RELATIONSHIP_PROPERTIES", ["description"])

# Parsing configuration
PROCESS_TABLE = os.getenv("PROCESS_TABLE", "false").lower() == "true"
TABLE_STRATEGY = os.getenv("TABLE_STRATEGY", "fast")
CHUNK_SIZE = os.getenv("CHUNK_SIZE", 500)
CHUNK_OVERLAP = os.getenv("CHUNK_OVERLAP", 50)
