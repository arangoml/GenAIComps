# Copyright (C) 2024 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import os

# ArangoDB configuration
ARANGO_URL = os.getenv("ARANGO_URL", "http://localhost:8529")
ARANGO_USERNAME = os.getenv("ARANGO_USERNAME", "root")
ARANGO_PASSWORD = os.getenv("ARANGO_PASSWORD", "test")
ARANGO_DB_NAME = os.getenv("ARANGO_DB_NAME", "_system")

# ArangoDB graph configuration
USE_ONE_ENTITY_COLLECTION = os.getenv("USE_ONE_ENTITY_COLLECTION", True)
INSERT_ASYNC = os.getenv("INSERT_ASYNC", False)
ARANGO_BATCH_SIZE = os.getenv("ARANGO_BATCH_SIZE", 500)

# Text Generation Inference configuration
TGI_LLM_ENDPOINT = os.getenv("TGI_LLM_ENDPOINT", "http://localhost:8080")
TGI_LLM_MAX_NEW_TOKENS = os.getenv("TGI_LLM_MAX_NEW_TOKENS", 512)
TGI_LLM_TOP_K = os.getenv("TGI_LLM_TOP_K", 40)
TGI_LLM_TOP_P = os.getenv("TGI_LLM_TOP_P", 0.9)
TGI_LLM_TEMPERATURE = os.getenv("TGI_LLM_TEMPERATURE", 0.8)
TGI_LLM_TIMEOUT = os.getenv("TGI_LLM_TIMEOUT", 600)

# Text Embeddings Inference configuration
TEI_EMBEDDING_ENDPOINT = os.getenv("TEI_EMBEDDING_ENDPOINT")
HUGGINGFACEHUB_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")
TEI_EMBED_MODEL = os.getenv("TEI_EMBED_MODEL", "BAAI/bge-base-en-v1.5")

# OpenAI configuration (alternative to TGI & TEI)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_EMBED_MODEL = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")
OPENAI_EMBED_DIMENSIONS = os.getenv("OPENAI_EMBED_DIMENSIONS", 512)
OPENAI_CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o")
OPENAI_CHAT_TEMPERATURE = os.getenv("OPENAI_CHAT_TEMPERATURE", 0)

# LLMGraphTransformer configuration
SYSTEM_PROMPT_PATH = os.getenv("SYSTEM_PROMPT_PATH")
ALLOWED_NODES = os.getenv("ALLOWED_NODES", [])
ALLOWED_RELATIONSHIPS = os.getenv("ALLOWED_RELATIONSHIPS", [])
NODE_PROPERTIES = os.getenv("NODE_PROPERTIES", ["description"])
RELATIONSHIP_PROPERTIES = os.getenv("RELATIONSHIP_PROPERTIES", ["description"])
