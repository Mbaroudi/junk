#!/usr/bin/env python
#coding: utf-8

import tweepy
import re

CONSUMER_KEY = "KBPPw58SVgIgnIjltv889A"
CONSUMER_SECRET = "kH9UCyRhQiquP8jXkvIWH0xpezCHAl9xknvT4rks"

ACCESS_KEY = "20695488-0ERLzheHs9mTIq5NNlmB0jxxFFsc4I9I0rcbbY3Wi"
ACCESS_SECRET = "8kzFkmHjvvDsXTPsrUE1wYEfvMBVWbEwDhnQr4ZUzg"

def getwords(text):
	r"""
	Разделяет слова (наборы букв без разделителей)

	>>> getwords("What does tiki-wiki mean?")
	['what', 'does', 'tiki', 'wiki', 'mean']
	"""
	splitter = re.compile(r'\W*', re.U)
	words = [ s for s in splitter.split(text) if s ]

	return [word.lower() for word in words]	

class Twitter:
	#r""" 
	#Loads user and his friends/followers stats from twitter
	#"""

	def __init__(self,username):
		auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
		auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
		self.api = tweepy.API(auth)

		limit = self.api.rate_limit_status()['remaining_hits']
		print 'you have', limit, 'API calls remaining until next hour'

		self.user = self.api.get_user(username)
		print self.user.id, self.user.screen_name, "followers count = ", str(self.user.followers_count)
			
	def __del__(self):
		limit = self.api.rate_limit_status()['remaining_hits']
		print 'now you only have', limit, 'API calls.'

	def getwordcounts(self, user, count=5):
		r""" 
		Функция считает количество упоминаний каждого слова в count сообщениях пользователя user
		"""

		wc={}

		for status in tweepy.Cursor(self.api.user_timeline, id = user.id).items(count):
			words = getwords(status.text)

			for word in words:
				wc.setdefault(word, 0)
				wc[word] += 1

		return user, wc

	def getfriends(self, count=5):
		friendlist = []
		for friend in tweepy.Cursor(self.api.friends).items(count):
			friendlist += [friend]
		return friendlist


# Run internal tests on methods in class Twitter				
if __name__ == "__main__":
	import doctest
	doctest.testmod()