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
ARANGO_BATCH_SIZE = int(os.getenv("ARANGO_BATCH_SIZE", 500))
ARANGO_GRAPH_NAME = os.getenv("ARANGO_GRAPH_NAME", "GRAPH")
ARANGO_USE_GRAPH_NAME = os.getenv("ARANGO_USE_GRAPH_NAME", "false").lower() == "true"

# Text Generation Inference configuration
TGI_LLM_ENDPOINT = os.getenv("TGI_LLM_ENDPOINT", "http://localhost:8080")
TGI_LLM_MAX_NEW_TOKENS = int(os.getenv("TGI_LLM_MAX_NEW_TOKENS", 512))
TGI_LLM_TOP_K = int(os.getenv("TGI_LLM_TOP_K", 40))
TGI_LLM_TOP_P = int(os.getenv("TGI_LLM_TOP_P", 0.9))
TGI_LLM_TEMPERATURE = int(os.getenv("TGI_LLM_TEMPERATURE", 0.8))
TGI_LLM_TIMEOUT = int(os.getenv("TGI_LLM_TIMEOUT", 600))

# Text Embeddings Inference configuration
TEI_EMBEDDING_ENDPOINT = os.getenv("TEI_EMBEDDING_ENDPOINT")
HUGGINGFACEHUB_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")
TEI_EMBED_MODEL = os.getenv("TEI_EMBED_MODEL", "BAAI/bge-base-en-v1.5")

# OpenAI configuration (alternative to TGI & TEI)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o")
OPENAI_CHAT_TEMPERATURE = int(os.getenv("OPENAI_CHAT_TEMPERATURE", 0))
OPENAI_EMBED_MODEL = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")
OPENAI_EMBED_DIMENSION = int(os.getenv("OPENAI_EMBED_DIMENSION", 768))
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
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 1500))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 100))
