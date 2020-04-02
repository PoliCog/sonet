"""
Write tweets to a file format.
"""

__author__ = "Ashwin"
__email__ = "gashwin1@umbc.edu"

import os
import csv
import json
import argparse

# Mongo Client library.
from lib.db.mongod import MongoClient

class Writer(object):
    def __init__(self, config, collection_name='twitter_data'):
        self.__DATABASE_INDEX_NAME = 'database'
        with open(config, "r") as twitter_config_file:
            config = json.load(twitter_config_file)

        self.__mongo_client = MongoClient(config[self.__DATABASE_INDEX_NAME],
                                          collection_name)

    def extract(self, file_loc, num_rows=0):
        # Get all the documents in the collection.
        fields = ['created_at', 'text', 'location']
        with open(file_loc, mode='w') as csv_file:
            # extrasaction='ignore' ignores other keys not in the fields list.
            csv_writer = csv.DictWriter(csv_file, fieldnames=fields, delimiter=';',
                                        extrasaction='ignore')
            csv_writer.writeheader()
            for idx, doc in enumerate(self.__mongo_client.read_all()):
                row = {'created_at': doc['created_at'],
                       'text': doc['text'],
                       'location': doc['user']['location']}
                csv_writer.writerow(row)
                if num_rows > 0 and idx >= num_rows:
                    break

DEFAULT_CONFIG = os.path.dirname(os.path.realpath(__file__)) + "/config/config.json"
parser = argparse.ArgumentParser(description='File Writing Wrapper.')
parser.add_argument('FILE_LOC', type=str, help='Output File Location.')
parser.add_argument('--num', type=int, default=0, help='Number of Tweets')
parser.add_argument('--collection', type=str, default='twitter_data', help='Collection Name.')
parser.add_argument('--config', action='store', type=str, default=DEFAULT_CONFIG,
                    dest='config', help='Configuration file.')
args = vars(parser.parse_args())

# Create a Writer.
wrt = Writer(args['config'], args['collection'])
wrt.extract(args['FILE_LOC'], args['num'])
