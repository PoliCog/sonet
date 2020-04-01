"""
Creates the connector to store and access the Mongo database.
"""

__author__ = 'ashwin'

# Python Mongo.
import pymongo
from pymongo.bulk import BulkWriteError
from pymongo.helpers import DuplicateKeyError


# This is the client for Mongo Database.
class MongoClient:
    def __init__(self, config):
        # Define the constants to be used.
        # These are the indexes to be used in the file containing
        # information about the mongo database.
        self.__ADDRESS_INDEX_STR = 'address'
        self.__PORT_INDEX_STR = 'port'

        # The database name.
        self.__DATABASE_NAME = 'twitter'
        self.__TWITTER_COLLECTION = 'twitter_data'

        # Define the hidden parameters.
        self.__m_client = None
        self.__m_db = None
        self.__m_t_collection = None

        if config is not None:
            self.__get_mongo_client(config)
        else:
            raise Exception("Filename containing database information has not been provided.")

        self.__get_db()
        self.__get_twitter_collection()

    def __get_mongo_client(self, config):
        if self.__m_client is None:
            self.__m_client = pymongo.MongoClient(config[self.__ADDRESS_INDEX_STR],
                                                  config[self.__PORT_INDEX_STR])
        return self.__m_client

    # Access the database.
    def __get_db(self):
        if self.__m_db is None:
            self.__m_db = self.__m_client[self.__DATABASE_NAME]

        return self.__m_db

    # Access the twitter collection.
    def __get_twitter_collection(self):
        if self.__m_t_collection is None:
            self.__m_t_collection = self.__m_db[self.__TWITTER_COLLECTION]

        return self.__m_t_collection

    ##########################################################################
    # In case the item does not have the parameter '_id' set then, then it is
    # automatically generated and assigned by MongoDB.
    ##########################################################################
    # Insert a document or bulk into twitter data collection.
    def insert(self, items, collection_name=None):
        # UnboundLocalError does not come up in case of an exception.
        collect = []
        try:
            if collection_name is None:
                collect = self.__m_t_collection.insert(items, continue_on_error=True)
            else:
                collect = self.__m_db[collection_name].insert(items, continue_on_error=True)
        except BulkWriteError:
            print("BulkWriteError: ", BulkWriteError.details)
        except DuplicateKeyError:
            print("DuplicateKeyError: ", DuplicateKeyError.details)

        return collect
