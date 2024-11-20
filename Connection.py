import json
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError


class MongoDBConnection:
    """A class to manage MongoDB connections."""

    def __init__(self, config_path="config.json"):
        """
        Initializes the MongoDBConnection class by loading configuration.
        
        :param config_path: Path to the JSON config file with MongoDB settings.
        """
        self.config_path = config_path
        self.uri, self.database_name = self._load_config()
        self.client = None
        self.db = None

    def _load_config(self):
        """
        Loads MongoDB configuration from a JSON file.
        
        :return: Tuple containing (uri, database_name).
        :raises FileNotFoundError: If the config file is missing.
        :raises KeyError: If required keys are missing in the config file.
        """
        try:
            with open(self.config_path, "r") as file:
                config = json.load(file)
                mongodb_config = config.get("mongodb", {})
                uri = mongodb_config.get("uri")
                database_name = mongodb_config.get("database_name")

                if not uri or not database_name:
                    raise KeyError("Missing 'uri' or 'database_name' in config.json")
                
                return uri, database_name
        except FileNotFoundError:
            print(f"Configuration file not found: {self.config_path}")
            raise
        except KeyError as e:
            print(f"Configuration error: {e}")
            raise

    def connect(self):
        """
        Establishes a connection to the MongoDB server.
        
        :return: A database instance if the connection is successful.
        :raises ServerSelectionTimeoutError: If the connection fails.
        """
        try:
            self.client = MongoClient(self.uri, serverSelectionTimeoutMS=5000)
            self.client.admin.command('ping')
            self.db = self.client[self.database_name]
            print(f"Connected to MongoDB database: {self.database_name}")
            return self.db
        except ServerSelectionTimeoutError as e:
            print(f"Failed to connect to MongoDB: {e}")
            raise

    def close(self):
        """
        Closes the connection to the MongoDB server.
        """
        if self.client:
            self.client.close()
            print("MongoDB connection closed.")
