#!/usr/bin/python
#-*-coding:utf-8-*-

"""
    This file is for initiate mongodb situation
    
    When you want to save book file in file system,then you don't need sharding cluster,that the database design is:
    database:tweets
    collections:tweet_detail
    fields:
        tweet_detail:
            tweet_id
            convo_url:string
            is_retweet:boolean
            user_id:string
            user_screen_name:string
            text:string
            created_at:timestamp
            image_url:vector
            num_retweets:int
            num_favorites:int
            is_first:boolean
            update_time:datetime
    index:
        tweet_id
        user_screen_name
        created_at

    So what this do is to delete books_fs if it has existed,and create index for it.
"""

import types
from pymongo.connection import MongoClient
from pymongo import ASCENDING, DESCENDING

DATABASE_NAME = "tweets"
client = None
DATABASE_HOST = "localhost"
DATABASE_PORT = 27017
INDEX = {
            # collection
            'tweet_detail':
            {
                (('user_screen_name', ASCENDING), ('tweet_id', DESCENDING)):
                    {
                        'name': 'user_id_time', 'unique': True
                    },
                'user_screen_name': {'name': 'user_screen_name'},
                'tweet_id': {'name': 'tweet_id'},
                'created_at': {'name': 'created_at'},
                }
        }

def drop_database(name_or_database):
    if name_or_database and client:
        client.drop_database(name_or_database)

def create_index():
    """
        create index for books_fs.book_detail
    """
    for k,v in INDEX.items():
        for key,kwargs in v.items():
            client[DATABASE_NAME][k].ensure_index(list(key) if type(key)==types.TupleType else key,**kwargs)

if __name__ == "__main__":
    client = MongoClient(DATABASE_HOST,DATABASE_PORT) 
    drop_database(DATABASE_NAME)
    create_index() 