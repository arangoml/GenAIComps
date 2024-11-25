import os
from config import COLLECTION_NAME
from arango_conn import ArangoClient
from pydantic import BaseModel
from comps import CustomLogger

logger = CustomLogger("arango_store")
logflag = os.getenv("LOGFLAG", False)

class PromptStore:

    def __init__(
        self,
        user: str,
    ):
        self.user = user

    def initialize_storage(self) -> None:
        logger.debug("get arango db client")
        self.db_client = ArangoClient.get_db_client()
      

        if self.db_client.has_collection(COLLECTION_NAME):
            self.collection = self.db_client.collection(COLLECTION_NAME)
        else:
            self.collection = self.db_client.create_collection(COLLECTION_NAME)
        
        self.collection = self.db_client.collection(COLLECTION_NAME)

    async def save_prompt(self, prompt):

        """Stores a new prompt into the storage.

        Args:
            prompt: The document to be stored. It should be a Pydantic model.

        Returns:
            str: The ID of the inserted prompt.

        Raises:
            Exception: If an error occurs while storing the prompt.
        """
        try:
            insert_prompt = {'user': prompt.user, 'content': prompt.prompt_text }
           
            inserted_prompt_metadata = self.collection.insert(insert_prompt)
            if  inserted_prompt_metadata and inserted_prompt_metadata.get('_id'):
                return inserted_prompt_metadata['_id']

        except Exception as error:
            logger.error(f"An error occurred: {str(error)}")
            raise error
        
    async def get_all_prompt_of_user(self) -> list[dict]:
        """Retrieves all prompts of a user from the collection.

        Returns:
            list[dict] | None: List of dict of prompts of the user, None otherwise.

        Raises:
            Exception: If there is an error while retrieving data.
        """
        try:
            prompt_list: list = []
            cursor=self.collection.find({'user': self.user})

            for document in cursor:
                prompt_list.append(document)
            return prompt_list

        except Exception as error:
            logger.error(f"An error occurred: {str(error)}")
            raise error

    async def get_user_prompt_by_id(self, prompt_id) -> dict | None:
        """Retrieves a user prompt from the collection based on the given prompt ID.

        Args:
            prompt_id (str): The ID of the prompt to retrieve.

        Returns:
            dict | None: The user prompt if found, None otherwise.

        Raises:
            Exception: If there is an error while retrieving data.
        """
        try:
           
            response: dict | None =self.collection.get({'_id': str(prompt_id)})
            logger.info(response)
            if response:
                return response["content"]
            return None

        except Exception as error:
            logger.error(f"An error occurred: {str(error)}")
            raise error

    async def prompt_search(self, keyword) -> list | None:
        """Retrieves prompt from the collection based on keyword provided.

        Args:
            keyword (str): The keyword of prompt to search for.

        Returns:
            list | None: The list of relevant prompt if found, None otherwise.

        Raises:
            Exception: If there is an error while searching data.
        """
        try:
            # Create an ArangoSearch view.
            self.db_client.create_arangosearch_view(
                    name='arangosearch_view',
                    properties={'cleanupIntervalStep': 0}
                )
            # Create a text index if not already created
            self.collection.create_index([("$**", "text")])
            # Perform text search
            results = self.collection.find({"$text": {"$search": keyword}}, {"score": {"$meta": "textScore"}})
            sorted_results = results.sort([("score", {"$meta": "textScore"})])

            # Return a list of top 5 most relevant data
            relevant_data = await sorted_results.to_list(length=5)

            # Serialize data and return
            serialized_data = [
                {"id": str(doc["_id"]), "prompt_text": doc["prompt_text"], "user": doc["user"], "score": doc["score"]}
                for doc in relevant_data
            ]

            return serialized_data

        except Exception as error:
            logger.error(f"An error occurred: {str(error)}")
            raise error
        

    async def delete_prompt(self, prompt_id) -> bool:
        """Delete a prompt from collection by given prompt_id.

        Args:
            prompt_id(str): The ID of the prompt to be deleted.

        Returns:
            bool: True if prompt is successfully deleted, False otherwise.

        Raises:
            KeyError: If the provided prompt_id is invalid:
            Exception: If any errors occurs during delete process.
        """
        try:
            
            result : dict | None = self.collection.delete(prompt_id)
            return result

        except Exception as error:
            logger.error(f"An error occurred: {str(error)}")
            raise error
