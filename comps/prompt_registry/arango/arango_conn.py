# Copyright (C) 2024 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

from arango import ArangoClient as PythonArangoClient
from arango.database import StandardDatabase
from config import ARANGO_URL, ARANGO_PASSWORD, ARANGO_USERNAME, ARANGO_DB_NAME


class ArangoClient:
    conn_url = ARANGO_URL

    @staticmethod
    def get_db_client() -> StandardDatabase:
        try:
            # Create client
            client = PythonArangoClient(hosts=ArangoClient.conn_url)

            # First connect to _system database
            sys_db = client.db("_system", username=ARANGO_USERNAME, password=ARANGO_PASSWORD, verify=True)

            # Create target database if it doesn't exist
            if not sys_db.has_database(ARANGO_DB_NAME):
                sys_db.create_database(ARANGO_DB_NAME)

            # Now connect to the target database
            db = client.db(ARANGO_DB_NAME, username=ARANGO_USERNAME, password=ARANGO_PASSWORD, verify=True)

            return db

        except Exception as e:
            print(e)
            raise e
