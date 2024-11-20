from config import COLLECTION_NAME
from arango_conn import ArangoClient
from pydantic import BaseModel


class FeedbackStore:

    def __init__(
        self,
        user: str,
    ):
        self.user = user

    def initialize_storage(self) -> None:
        self.db_client = ArangoClient.get_db_client()
        self.collection = self.db_client[COLLECTION_NAME]

    def save_feedback(self, feedback_data: BaseModel) -> str:
        """Stores a new feedback data into the storage.

        Args:
            feedback_data (object): The document to be stored.

        Returns:
            str: The ID of the inserted feedback data.

        Raises:
            Exception: If an error occurs while storing the feedback_data.
        """
        try:
            model_dump = feedback_data.model_dump(by_alias=True, mode="json", exclude={"feedback_id"})
            model_dump["_id"] = f"{self.collection.name}/{feedback_data.feedback_id}"

            inserted_feedback_data = self.collection.insert(model_dump)
            
            feedback_id = str(inserted_feedback_data.inserted_id)
            
            return feedback_id

        except Exception as e:
            print(e)
            raise Exception(e)

    def update_feedback(self, feedback_data) -> bool:
        """Update a feedback data in the collection with given id.

        Args:
            feedback_id (str): The ID of the data to be updated.
            updated_data (object):  The data to be updated in the entry.

        Returns:
            bool: True if the data updated successfully, False otherwise.
        """
        _key = feedback_data.feedback_id 

        document = self.collection.get(_key)

        if document is None:
            raise Exception(f"Document with ID: {_key} not found.")
        
        if document["chat_data"]["user"] != self.user:
            raise Exception(f"User mismatch. Document with ID: {_key} does not belong to user: {self.user}")

        try:
            model_dump = feedback_data.feedback_data.model_dump(by_alias=True, mode="json")
            
            result = self.collection.update(
                {"_key": _key, "feedback_data": model_dump},
                merge=True,
                keep_none=False,
            )

            print(result)
        except Exception as e:
            print(e)
            raise Exception("Not able to update the data.")

    def get_all_feedback_of_user(self) -> list[dict]:
        """Retrieves all feedback data of a user from the collection.

        Returns:
            list[dict] | None: List of dict of feedback data of the user, None otherwise.

        Raises:
            Exception: If there is an error while retrieving data.
        """
        try:
            feedback_data_list: list = []

            cursor = """
                FOR doc IN @@collection
                    FILTER doc.chat_data.user == @user
                    RETURN UNSET(doc, "feedback_data")
            """

            cursor = self.db_client.aql.execute(cursor, bind_vars={"@@collection": self.collection.name, "user": self.user})

            for document in cursor:
                document["feedback_id"] = str(document["_key"])
                del document["_key"]
                feedback_data_list.append(document)

            return feedback_data_list

        except Exception as e:
            print(e)
            raise Exception(e)

    def get_feedback_by_id(self, feedback_id) -> dict | None:
        """Retrieves a user feedback data from the collection based on the given feedback ID.

        Args:
            feedback_id (str): The ID of the feedback data to retrieve.

        Returns:
            dict | None: The user's feedback data if found, None otherwise.

        Raises:
            Exception: If there is an error while retrieving data.
        """
        response = self.collection.get(feedback_id)

        if response is None:
            raise Exception(f"Feedback with ID: {feedback_id} not found.")
        
        if response["chat_data"]["user"] != self.user:
            raise Exception(f"User mismatch. Feedback with ID: {feedback_id} does not belong to user: {self.user}")

        del response["_id"]

        return response

    def delete_feedback(self, feedback_id) -> bool:
        """Delete a feedback data from collection by given feedback_id.

        Args:
            feedback_id(str): The ID of the feedback data to be deleted.

        Returns:
            bool: True if feedback is successfully deleted, False otherwise.

        Raises:
            KeyError: If the provided feedback_id is invalid:
            Exception: If any errors occurs during delete process.
        """
        response = self.collection.get(feedback_id)

        if response is None:
            raise Exception(f"Feedback with ID: {feedback_id} not found.")
        
        if response["chat_data"]["user"] != self.user:
            raise Exception(f"User mismatch. Feedback with ID: {feedback_id} does not belong to user: {self.user}")

        try:
            response = self.collection.delete(feedback_id)

            return True
        except Exception as e:
            print(e)
            raise Exception("Not able to delete the data.")
