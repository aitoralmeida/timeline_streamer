# -*- coding: utf-8 -*-
"""
Created on Mon Nov 02 11:51:52 2015

@author: aitor
"""

from datetime import datetime
import json
import os
import sys
import time

import twitter


# last processed tweet ids
last_ids = {}
# Screen names to follow
screen_names = []

# Get credentials and log in
credentials = json.load(open('credentials.json', 'r'))
CONSUMER_KEY = credentials['consumer_key']
CONSUMER_SECRET = credentials['consumer_secret']
OAUTH_TOKEN = credentials['oauth_token']
OAUTH_TOKEN_SECRET = credentials['oauth_secret']

auth = twitter.oauth.OAuth(OAUTH_TOKEN, OAUTH_TOKEN_SECRET,
                           CONSUMER_KEY, CONSUMER_SECRET)
twitter_api = twitter.Twitter(auth=auth) 
        
def save_statuses(screen_name, last_id, statuses):
    now = datetime.now()
    folder = './statuses/%s-%s-%s' % (now.year, now.month, now.day)
    if not os.path.isdir(folder):
        os.makedirs(folder)
    log_msg('  -Saving %s tweets for %s' % (len(statuses), screen_name))
    filename = '%s/%s-%s.json' % (folder, screen_name, last_id)
    json.dump(statuses, open(filename, 'w'))
        
def recover_statuses(count = 200):
    log_msg('Recovering tweets for %s users...' % len(screen_names))
    for screen_name in screen_names:
        statuses  = twitter_api.statuses.user_timeline(screen_name = screen_name, count = count, since_id = last_ids[screen_name])
        if len(statuses) > 0:        
            last_ids[screen_name] = max([s['id'] for s in statuses])
            save_statuses(screen_name, last_ids[screen_name], statuses) 
    
    json.dump(last_ids, open('last_ids.json', 'w'))
    
def initialization():
    last_ids = {}
    # Get screen names to process
    log_msg('Loading the screen names to process...')
    screen_names = json.load(open('screen_names.json', 'r'))   
    # Get last processed tweet ids
    log_msg('Loading the last processed ids...')
    try:
        last_ids = json.load(open('last_ids.json', 'r'))
    except:
        # If no last ids on record, get the most recent one for each user
        log_msg('  -No last_ids found, recovering the most recent status for each user')
        for screen_name in screen_names:
            statuses  = twitter_api.statuses.user_timeline(screen_name = screen_name, count = 1)
            # If the account does not have any tweet, the last id is 0
            try:
                last_ids[screen_name] = max([s['id'] for s in statuses])
            except: 
                last_ids[screen_name] = 0
            if len(statuses) > 0:  
                save_statuses(screen_name, last_ids[screen_name], statuses)  
    
    return screen_names, last_ids
            
def log_msg(msg):
    now = datetime.now()
    print '%s-%s %s:%s:%s %s' % (now.month, now.day, now.hour, now.minute, now.second, msg)
    
if __name__ == '__main__':
    log_msg('Initializing ...')
    screen_names, last_ids = initialization()
    while True:
       recover_statuses(count = 200) 
       log_msg('Waiting 5 mins ...')
       sys.stdout.flush()
       time.sleep(60 * 5)
    
    
    