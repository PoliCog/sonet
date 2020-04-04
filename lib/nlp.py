"""
Basic NLP pipeline components to analyze twitter data.
"""

__author__ = "Ashwin"
__email__ = "gashwin1@umbc.edu"

import os
import csv
import json
import argparse
from tabulate import tabulate
import pandas as pd

# Mongo Client library.
from lib.db.mongod import MongoClient


class Dataset(object):
    """
    Class to manage a set of tweets and related metadata.
    """
    def __init__(self, config, collection_name='twitter_data', dataset_size=0):
        self.__DATABASE_INDEX_NAME = 'database'
        with open(config, "r") as twitter_config_file:
            config = json.load(twitter_config_file)

        self.__mongo_client = MongoClient(config[self.__DATABASE_INDEX_NAME],
                                          collection_name)
        self.__length = dataset_size
        self.__data = self.__read_data(self.__length)

    def __len__(self):
        return self.__length

    def __getitem__(self, key):
        return self.__data.iloc[key]

    def __read_data(self, num_rows=0):
        # Get all the documents in the collection.
        fields = ['created_at', 'text', 'location']
        data_rows = []
        for idx, doc in enumerate(self.__mongo_client.read_all()):
            data_rows.append([doc['created_at'], doc['text'],
                              doc['user']['location']])
            if num_rows > 0 and idx >= num_rows:
                break

        df = pd.DataFrame(data_rows)
        df.columns = fields
        return df

    def get_data(self, num_rows=0):
        if num_rows <= 0:
            return self.__data
        else:
            return self.__data.iloc[0: num_rows]

    def refresh(self):
        self.__data = self.__read_data(num_rows)

    @staticmethod
    def print_frame(df):
        print(tabulate(df, headers='keys', tablefmt='psql'))
