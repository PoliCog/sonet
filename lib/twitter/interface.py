"""
Perform all the operations with the Twitter Api.
Set of Operations:
1. Authenticate with Twitter API.
2. Get the API Object for search and download tweets.
3. Search for tweets.
"""

__author__ = 'Ashwin'
__email__ = "gashwin1@umbc.edu"

# Standard Libs.
import time
import json
from tqdm import tqdm

# Twitter.
import tweepy
from lib.db.mongod import MongoClient


class TwitterAPI():
    def __init__(self, auth_keys):
        # Defining the constants that are being used.
        ######################################################
        self.__CONSUMER_KEY_STR = 'consumer_key'
        self.__CONSUMER_SECRET_STR = 'consumer_secret'
        self.__ACCESS_TOKEN_STR = 'access_token'
        self.__ACCESS_TOKEN_SECRET_STR = 'access_token_secret'
        self.__t_auth = None
        self.t_api = None
        ######################################################

        # Generate Authorization keys.
        self.__t_auth = tweepy.OAuthHandler(auth_keys[self.__CONSUMER_KEY_STR],
                                            auth_keys[self.__CONSUMER_SECRET_STR])
        self.__t_auth.set_access_token(auth_keys[self.__ACCESS_TOKEN_STR],
                                       auth_keys[self.__ACCESS_TOKEN_SECRET_STR])
        # Generate the API.
        if self.__t_auth is not None:
                self.t_api = tweepy.API(self.__t_auth)
        else:
                raise Exception("API cannot be generated as O-Auth is not specified.")


# This is the interface for access twitter and work with the
# data.
class TwitterInterface():
    """
    The authorization keys which are in the parameter auth_keys should have
    the following index:
    1. consumer_key
    2. consumer_secret
    3. access_token
    4. access_token_secret
    """
    def __init__(self, config, collection_name='twitter_data'):
        # Defining the constants that are being used.
        ######################################################
        self.__AUTH_INDEX_NAME = 'auth'
        self.__DATABASE_INDEX_NAME = 'database'
        self.__twitter_api = []
        self.__MAX_TWEET_PER_PAGE = 100
        self.__MAX_MINUTES = 16
        self.__SLEEP_TIME = self.__MAX_MINUTES * 60

        # This is for API's.
        self.__api_gen = None
        ######################################################

        if config is None:
            raise Exception("Configuration is not available.")

        # Check the number of keys in the config.
        for auth_keys in config[self.__AUTH_INDEX_NAME]:
            self.__twitter_api.append(TwitterAPI(auth_keys))

        self.__curr_api = self.__get_api()

        # Setup the MongoClient, so that database operations can be performed.
        self.__collection = collection_name
        self.__mongo_client = MongoClient(config[self.__DATABASE_INDEX_NAME],
                                          self.__collection)

    # This is a generator to generate API from a circular queue.
    def __get_current_api(self):
        # When the rate limit is reached, there are two options.
        while True:
            # Switch to a new key.
            for api in self.__twitter_api:
                print("Switching API Keys...")
                yield api

            # OPTION 2:
            # Back off from querying by sleeping for sometime.
            print("Rate-limit reached & No more API's left, " \
                  "Sleeping for a " + str(self.__SLEEP_TIME) + " seconds.")

            # Once the API has been changed, continue collecting tweets.
            pbar = tqdm(range(self.__MAX_MINUTES))
            for i in pbar:
                time.sleep(60)
                pbar.set_description("Twitter Waiting Time (Minutes)")


    # Get a continuous stream of API's.
    def __get_api(self):
        if self.__api_gen is None:
            self.__api_gen = self.__get_current_api()

        return next(self.__api_gen)

    """
    This function searches twitter using the given query and returns a set of
    tweets.
    Parameters:
    :param max: The max number of tweets that need to be returned.
    :param query : The query string that is searched.
    :param rpp: The parameter is used for pagination.
    """
    # The search function is meant as a test function to check the results of the search query.
    # Use the search_n_insert function instead.
    def search_twitter(self, query, maximum=0, r_type="recent", inc_en=True, language="en"):
        t_list = []
        for ctr, tweet in enumerate(tweepy.Cursor(self.__curr_api.t_api.search, q=query,
                                                  rpp=self.__MAX_TWEET_PER_PAGE,
                                                  result_type=r_type, include_entities=inc_en,
                                                  lang=language).items()):

            # If the number of tweets in the list is greater than rpp.
            # Then return back the list.

            # Check if the maximum number of tweets have been reached.
            if (maximum > 0) and (ctr >= maximum):
                # Return the remaining list of tweets.
                if len(t_list) > 0:
                    yield t_list

                return

            """
            Convert this into a dictionary object which can be dumped into a json file.
            If the number is too large, do it in chunks.
            Chunking is implemented, so that insert into mongo do not become too expensive.
            """
            # Construct a hash out of the user_id and the date.
            # The assumption is that this should be unique ID for the tweet.
            #_t_id = hashlib.sha224(tweet.author.screen_name.encode('utf8') + str(tweet.created_at.ctime())).hexdigest()
            #t_item = {'_id': _t_id}
            t_item = {'_id': tweet.id}

            # Using a protected member to access the JSON object directly.
            t_item.update(tweet._json)
            t_list.append(t_item)

            # Return the Tweet in the form of a dictionary.
            if ((ctr+1) % self.__MAX_TWEET_PER_PAGE) == 0:
                yield t_list

                # Clear the list.
                del t_list
                t_list = []

    # A simple wrapper function to search twitter and then insert the tweet in the database.
    def search_n_insert(self, query, maximum=0, collection_name=None,
                        rtype="recent", include_en=True, lang="en"):
        while True:
            try:
                for t_list in self.search_twitter(query, maximum, r_type=rtype,
                                                  inc_en=include_en, language=lang):
                    # Once the list of tweets has been created, insert it into the database.
                    if len(t_list) > 0:
                        if collection_name is None:
                            self.__mongo_client.insert(t_list)
                        else:
                            self.__mongo_client.insert(t_list, collection_name)

                # Break when all tweets have been collected.
                break
            except tweepy.TweepError as error:
                """
                 The errors that have been handled are:
                 1. Code 429: Rate limit exceeded. The solution is to sleep for a 15 minute period, till
                    Twitter reset the rate.
                """
                code = int(error.reason.split("\n")[0].split(" ")[-1])

                # The rate-limit has been reached.
                if code == 429:
                    self.__curr_api = self.__get_api()

        return 0
