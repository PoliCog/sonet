#!/usr/bin/python

__author__ = 'ashwin'
__email__ = 'gashwin1@umbc.edu'

"""
SONET is a project to analyse twitter data stream.

The tool is a command line tool which accesses the twitter using the Twitter API
and can search for various tweets. The tweets are then stored in a MongoDB.
"""

"""
The command line is implemented using the python library 'click'.
"""

import click
import json
import os
from lib.twitter.interface import TwitterInterface

DEFAULT_CONFIG = os.path.dirname(os.path.realpath(__file__)) + "/config/config.json"
def get_interface(filename, collection_name='twitter_data'):
    with open(filename, "r") as twitter_config_file:
        config = json.load(twitter_config_file)

    ti = TwitterInterface(config)
    return ti

# Create a group for commands.
@click.group()
def cli():
    return


# Search twitter and get tweets related to the query.
@cli.command()
@click.argument('query')
@click.option('--config', default=DEFAULT_CONFIG, help='Configuration file with Authorization keys.')
@click.option('-n', default=1, help='The number of tweets to be returned.')
def search(query, config, n):
    ti = get_interface(config)
    for t_list in ti.search_twitter(query, n):
        for tweet in t_list:
            print(tweet)
            print(tweet['text'])


# Search twitter for a list of query terms provided in a file.
@cli.command()
@click.argument('filename')
@click.option('--config', default=DEFAULT_CONFIG, help='Configuration file with Authorization keys.')
@click.option('-n', default=1, help='The number of tweets to be returned per search term.')
def fsearch(filename, config, n):
    ti = get_interface(config)
    with open(filename, "r") as t_file:
        for query in t_file:
            query = query.split("\n")[0]
            for t_list in ti.search_twitter(query, n):
                for tweet in t_list:
                    print(tweet['text'])


@cli.command()
@click.argument('query')
@click.option('--config', default=DEFAULT_CONFIG, help='Configuration file with Authorization keys.')
@click.option('-n', default=0, help='The number of tweets to be returned.')
@click.option('-c', default=None, help='Store in a new collection in MongoDB.')
def insert(query, config, n, c):
    ti = get_interface(config)
    ti.search_n_insert(query, n, c)


# Insert from a list query terms in a filename.
@cli.command()
@click.argument('filename')
@click.option('--config', default=DEFAULT_CONFIG, help='Configuration file with Authorization keys.')
@click.option('-n', default=0, help='The number of tweets to be returned.')
@click.option('-c', default=None, help='Store in a new collection in MongoDB.')
def finsert(filename, config, n, c):
    ti = get_interface(config, c)
    with open(filename, "r") as t_file:
        for query in t_file:
            query = query.split("\n")[0]
            ti.search_n_insert(query, n)

# Call the basic function.
cli()
