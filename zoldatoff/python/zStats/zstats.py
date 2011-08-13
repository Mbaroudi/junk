#!/usr/bin/env python

import tweepy
import sqlite3

auth = tweepy.OAuthHandler("KBPPw58SVgIgnIjltv889A", "kH9UCyRhQiquP8jXkvIWH0xpezCHAl9xknvT4rks")
auth.set_access_token("20695488-0ERLzheHs9mTIq5NNlmB0jxxFFsc4I9I0rcbbY3Wi", "8kzFkmHjvvDsXTPsrUE1wYEfvMBVWbEwDhnQr4ZUzg")
api = tweepy.API(auth)


user = api.get_user('zoldatoff')

print (user.screen_name, "followers count = " + str(user.followers_count))

friendList = []

for friend in user.friends():
    #print(friend.screen_name, friend.followers_count)
	friendList += [friend]
	
friendList.sort(key=lambda e: e.friends_count, reverse=True)	

for friend in friendList:
	print("id = " + str(friend.id), "name = " + friend.screen_name, "friends count = " + str(friend.friends_count), "followers count = " + str(friend.followers_count))

#print friend.status.__dict__.keys()