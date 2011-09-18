#!/usr/bin/env python
#coding: utf-8

import tweepy
import re

CONSUMER_KEY = "KBPPw58SVgIgnIjltv889A"
CONSUMER_SECRET = "kH9UCyRhQiquP8jXkvIWH0xpezCHAl9xknvT4rks"

ACCESS_KEY = "20695488-0ERLzheHs9mTIq5NNlmB0jxxFFsc4I9I0rcbbY3Wi"
ACCESS_SECRET = "8kzFkmHjvvDsXTPsrUE1wYEfvMBVWbEwDhnQr4ZUzg"

def getwords(text):
	#words = re.compile(r'[^A-Z^a-z^А-Я^а-я]+').split(text)
	splitter = re.compile(r'\W*', re.U)
	words = [ s for s in splitter.split(text) if s ]
	#print len(words)

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
		wc={}

		for status in tweepy.Cursor(self.api.user_timeline, id = user.id).items(count):
			print user.screen_name, status.text
			words = getwords(status.text)

			for word in words:
				#print word
				wc.setdefault(word, 0)
				wc[word] += 1

		return user, wc

	def getfriends(self, count=5):
		friendlist = []
		for friend in tweepy.Cursor(self.api.friends).items(count):
			print friend.screen_name
			friendlist += [friend]
		return friendlist
				

import codecs
code = 'utf-8'
out = codecs.open('words.txt','w',code)

apcount = {}
wordcounts = {}
z = Twitter('zoldatoff')
fiendlist = z.getfriends()

for friend in fiendlist:
	user, wc = z.getwordcounts(friend)
	wordcounts[user] = wc
	for word, count in wc.items():
		apcount.setdefault(word, 0)
		if count > 1:
			apcount[word] += 1

wordlist = []
for w,bc in apcount.items():
	frac = float(bc) / len(fiendlist)
	if 0.1 < frac < 0.5:
		wordlist.append(w)

print apcount		
print wordlist

#out = file('words.txt', 'w')
out.write('User')
for word in wordlist: 
	print type(word)
	out.write('\t%s' % word)
out.write('\n')

for user, wc in wordcounts.items():
	out.write(user.screen_name)
	for word in wordlist:
		if word in wc: out.write('\t%d' % wc[word])
		else: out.write('\t0')
	out.write('\n')
