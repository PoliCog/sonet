SONET
=====
This is a project to understand and analyze the following:

1. How a message flows in a social network
2. Isolating user profiles for a specific topic.
3. Summarizing Statistical data over a geographical area.
   -- a. Isolating messages from a specific geographic area.
   -- b. Using Message summarization
   -- c. Performing clustering on these summaries.

SYSTEM REQUIREMENTS
===================
The framework is designed using Python & MongoDB.
The python libraries required are:
1. Tweepy - Python library to use the Twitter API
   http://tweepy.readthedocs.org/en/v3.2.0/#
2. Pymongo - Python library to access MongoDB.

SETTING UP THE SYSTEM
=====================
_MongoDB_

1. Update Mongo conf.
   ```
   MongoDB config file - /etc/mongodb.conf
   Replace:
   bind_ip = 127.0.0.1
   with
   bind_ip = 127.0.0.1,<ip_address of mongodb>
   ```

2. Create the following in MongoDB
   ```
   a. Create a db 'twitter'. All the collections are created in this database.
   b. Create a collection 'twitter_data' which contains all the twitter data.
      Index twitter_data on the following:
      --  Location
      --  Tweet (text)
      --  User ID (Twitter Handle)
      --  Geo
   ```
