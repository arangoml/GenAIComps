# Copyright (C) 2024 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

# import motor.motor_asyncio as motor
from arango import ArangoClient as PythonArangoClient
from arango.database import StandardDatabase
from config import DB_NAME, ARANGODB_HOST, ARANGODB_PORT, ARANGODB_PASSWORD, ARANGODB_USERNAME,OPEA_DB_NAME

class ArangoClient:
    conn_url = f"http://{ARANGODB_HOST}:{ARANGODB_PORT}/" # http://localhost:8529/

    @staticmethod
    def get_db_client() -> StandardDatabase:
        try:
            client = PythonArangoClient(hosts=ArangoClient.conn_url)
            db = client.db(DB_NAME, username=ARANGODB_USERNAME, password=ARANGODB_PASSWORD, verify=True)
            # sys_db = client.db('_system', username='root', password='passwd')
            if not db.has_database(OPEA_DB_NAME):
                db.create_database(OPEA_DB_NAME)
            
            db_opea = client.db(OPEA_DB_NAME, username=ARANGODB_USERNAME, password=ARANGODB_PASSWORD, verify=True)

            return db_opea

        # except Exception as e:
        #     print(e)
        #     raise Exception()
        except Exception as e:
            print(f"Failed to connect to ArangoDB: {e}")
            raise