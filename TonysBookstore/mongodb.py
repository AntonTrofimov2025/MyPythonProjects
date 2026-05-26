from pymongo import MongoClient

class Mongo:
    def __init__(self):
        self.__client = MongoClient(
            "mongodb://ich_editor:verystrongpassword"
            "@mongo.itcareerhub.de/?readPreference=primary"
            "&ssl=false&authMechanism=DEFAULT&authSource=ich_edit"
            )
        self.__db = self.__client['ich_edit']
        self.__bookstore = self.__db['bookstore_logs_searches_anton_t']

    @property
    def my_bookstore(self):
        return self.__bookstore

    def __enter__(self):
        self.__client.admin.command("ping")
        print("Mongo Connection successful!")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.__client:
            self.__client.close()
            print("Mongo Connection closed.")
