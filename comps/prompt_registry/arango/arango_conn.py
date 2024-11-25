import os
from arango import ArangoClient as PythonArangoClient
from arango.database import StandardDatabase
from config import DB_NAME, ARANGODB_HOST, ARANGODB_PORT, ARANGODB_PASSWORD, ARANGODB_USERNAME,OPEA_DB_NAME
from comps import CustomLogger

logger = CustomLogger("arango_conn")
logflag = os.getenv("LOGFLAG", False)

class ArangoClient:
    conn_url = f"http://{ARANGODB_HOST}:{ARANGODB_PORT}/"

    @staticmethod
    def get_db_client() -> StandardDatabase:
        try:
            client = PythonArangoClient(hosts=ArangoClient.conn_url)
            logger.debug("starting connection to db with name:{name}, username:{username}".format(name=DB_NAME, username=ARANGODB_USERNAME))
            db = client.db(DB_NAME, username=ARANGODB_USERNAME, password=ARANGODB_PASSWORD, verify=True)
            logger.debug("successfully connected to db with name:{name}, username:{username}".format(name=DB_NAME, username=ARANGODB_USERNAME))
            if not db.has_database(OPEA_DB_NAME):
                logger.debug("No OPEA DB detected, so creating one")
                db.create_database(OPEA_DB_NAME)
                logger.debug("Created OPEA DB")
            
            db_opea = client.db(OPEA_DB_NAME, username=ARANGODB_USERNAME, password=ARANGODB_PASSWORD, verify=True)
            logger.debug("successfully connected to db with name:{name}, username:{username}".format(name=DB_NAME, username=ARANGODB_USERNAME))

            return db_opea

        except Exception as error:
            logger.error(f"An error occurred: {str(error)}")
            raise error