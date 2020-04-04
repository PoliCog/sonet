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
from pprint import pprint
from lib.twitter.interface import TwitterInterface

DEFAULT_CONFIG = os.path.dirname(os.path.realpath(__file__)) + "/config/config.json"
DEFAULT_AUTH = os.path.dirname(os.path.realpath(__file__)) + "/config/auth.json"

def get_interface(config_file, auth_file, collection_name='twitter_data'):
    with open(config_file, "r") as twitter_config_file:
        config = json.load(twitter_config_file)

    with open(auth_file, "r") as twitter_auth_file:
        auth = json.load(twitter_auth_file)

    ti = TwitterInterface(config, auth)
    return ti

# Create a group for commands.
@click.group()
def cli():
    return


# Search twitter and get tweets related to the query.
@cli.command()
@click.argument('query')
@click.option('--config', default=DEFAULT_CONFIG, help='Configuration file.')
@click.option('--auth', default=DEFAULT_AUTH, help='Authorization Keys.')
@click.option('-n', default=1, help='The number of tweets to be returned.')
@click.option('--full', is_flag=True, help='The number of tweets to be returned.')
def search(query, config, auth, n, full):
    print(auth)
    ti = get_interface(config, auth)
    for t_list in ti.search_twitter(query, n):
        for tweet in t_list:
            if full:
                print(json.dumps(tweet, indent=4, sort_keys=True))
            else:
                print(tweet['user']['screen_name'] + ": " + tweet['text'])


# Search twitter for a list of query terms provided in a file.
@cli.command()
@click.argument('filename')
@click.option('--config', default=DEFAULT_CONFIG, help='Configuration file.')
@click.option('--auth', default=DEFAULT_AUTH, help='Authorization Keys.')
@click.option('-n', default=1, help='The number of tweets to be returned per search term.')
@click.option('--full', is_flag=True, help='The number of tweets to be returned.')
def fsearch(filename, config, auth, n):
    ti = get_interface(config, auth)
    with open(filename, "r") as t_file:
        for query in t_file:
            query = query.split("\n")[0]
            for t_list in ti.search_twitter(query, n):
                for tweet in t_list:
                    if full:
                        print(json.dumps(tweet, indent=4, sort_keys=True))
                    else:
                        print(tweet['user']['screen_name'] + ": " + tweet['text'])


@cli.command()
@click.argument('query')
@click.option('--config', default=DEFAULT_CONFIG, help='Configuration file.')
@click.option('--auth', default=DEFAULT_AUTH, help='Authorization Keys.')
@click.option('-n', default=0, help='The number of tweets to be returned.')
@click.option('-c', default=None, help='Store in a new collection in MongoDB.')
def insert(query, config, auth, n, c):
    ti = get_interface(config, auth)
    ti.search_n_insert(query, n, c)


# Insert from a list query terms in a filename.
@cli.command()
@click.argument('filename')
@click.option('--config', default=DEFAULT_CONFIG, help='Configuration file.')
@click.option('--auth', default=DEFAULT_AUTH, help='Authorization Keys.')
@click.option('-n', default=0, help='The number of tweets to be returned.')
@click.option('-c', default=None, help='Store in a new collection in MongoDB.')
def finsert(filename, config, auth, n, c):
    ti = get_interface(config, auth)
    with open(filename, "r") as t_file:
        for query in t_file:
            query = query.split("\n")[0]
            ti.search_n_insert(query, n)

# Call the basic function.
cli()
