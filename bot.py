from __future__ import print_function
import os
import sys
import json
import logging
import tweepy
import thinkthread2

creds_file = 'credentials.json'

credentials = {}

if os.path.isfile(creds_file):
    with open(creds_file) as infile:
        credentials = json.load(infile)
else:
    print('Credentials not found. Run auth_setup.py first.')
    sys.exit(1)

auth = tweepy.OAuthHandler(credentials['ConsumerKey'],
                           credentials['ConsumerSecret'])
auth.set_access_token(credentials['AccessToken'],
                      credentials['AccessSecret'])

api = tweepy.API(auth)

def do_tweet(event, context):
    thread = thinkthread2.random_thread()
    status = None
    for post in thread:
        prev_id = status.id if status else None
        status = api.update_status(post, in_reply_to_status_id=prev_id)

    return thread[-1]

if __name__ == '__main__':
    print(do_tweet(None, None))
