# Copyright (C) 2024 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import os

# ArangoDB configuration
ARANGODB_URI = os.getenv("ARANGODB_URI", "http://localhost:8529")
ARANGODB_USERNAME = os.getenv("ARANGODB_USERNAME", "root")
ARANGODB_PASSWORD = os.getenv("ARANGODB_PASSWORD", "test")
ARANGODB_DATABASE = os.getenv("ARANGODB_DATABASE", "_system")

# Embedding model
EMBED_MODEL = os.getenv("EMBED_MODEL", "BAAI/bge-base-en-v1.5")

# Embedding endpoints
EMBED_ENDPOINT = os.getenv("TEI_EMBEDDING_ENDPOINT", "")
