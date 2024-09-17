from pymongo import MongoClient
class MongoDBHandler:
    def __init__(self, connection_string, database_name, collection_name):
        self.connection_string = connection_string
        self.client = MongoClient(self.connection_string)
        self.db = self.client[database_name]
        self.collection = self.db[collection_name]

    def insert_many(self, data):
        self.collection.insert_many(data)

    def insert_one(self, data):
        self.collection.insert_one(data)