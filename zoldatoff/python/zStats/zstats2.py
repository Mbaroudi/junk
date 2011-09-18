#!/usr/bin/env python

import tweepy
import sqlite3

auth = tweepy.OAuthHandler("KBPPw58SVgIgnIjltv889A", "kH9UCyRhQiquP8jXkvIWH0xpezCHAl9xknvT4rks")
auth.set_access_token("20695488-0ERLzheHs9mTIq5NNlmB0jxxFFsc4I9I0rcbbY3Wi", "8kzFkmHjvvDsXTPsrUE1wYEfvMBVWbEwDhnQr4ZUzg")
api = tweepy.API(auth)

class zstats:
		def __init__(self,dbname,username):
			limit = api.rate_limit_status()['remaining_hits']
			print 'you have', limit, 'API calls remaining until next hour'
			self.user = api.get_user(username)
			#self.friendList = []
			print (self.user.id, self.user.screen_name, "followers count = " + str(self.user.followers_count))
			self.con=sqlite3.connect(dbname)
			
		def __del__(self):
			self.con.close( )
			limit= api.rate_limit_status()['remaining_hits']
			print 'now you only have', limit, 'API calls.'
			
		def db_commit(self):
			self.con.commit( )
			
		def db_create(self):
			self.con.execute('create table friendlink(id, friendid)')	
			self.con.execute('create table friend(id, name, friends_count, followers_count)')			
			self.db_commit( )
			
		def db_clear(self):	
			self.con.execute('delete from friendlink')	
			self.con.execute('delete from friend')			
			self.db_commit( )
			
		def db_addfriend(self, friend):
			cur = self.con.execute("insert into friend(id, name, friends_count, followers_count) \
							  		values (%d, '%s', %d, %d)" % (friend.id, friend.screen_name, friend.friends_count, friend.followers_count))			
			self.db_commit( )		
			
		def db_addfriendlink(self, id, friendid):
			cur = self.con.execute("insert into friendlink(id, friendid) \
							  		values (%d, %d)" % (id, friendid))			
			self.db_commit( )
			
		def db_getfriend(self, id):
			cur = self.con.execute("select id, name, friends_count, followers_count \
									from friend \
									where id = %d" % id).fetchone()
			if cur != None:
				print(cur[0], cur[1], cur[2], cur[3])						
				
		def db_getfriendlist(self, id):
			cur = self.con.execute("select l.id, f.name \
									from friendlink l \
										 inner join friend f on l.friendid = f.id \
									where l.id = %d" % id)
			friendlist = []
			for row in cur:
				friendlist += [row[1]]
				print(row[0], row[1])
				
			return friendlist
			
		def t_getuserfriends(self):
			for friend in self.user.friends():
				self.db_addfriend(friend)
				self.db_addfriendlink(self.user.id, friend.id)
				
		def t_getfriends(self):
			friendlist = self.db_getfriendlist(self.user.id)
			for item in friendlist:			
				user = api.get_user(item)
				print(user.id, item)
				
				for friend in tweepy.Cursor(api.friends, id=item).items(5):
					self.db_addfriend(friend)
					self.db_addfriendlink(user.id, friend.id)				

			#self.friendList.sort(key=lambda e: e.friends_count, reverse=True)

			
z = zstats('zstats', 'zoldatoff')
#z.db_create( )	
#z.db_clear( )	
#z.t_getuserfriends( )
#z.t_getfriends( )
#z.db_getfriend(15850593)
z.db_getfriendfriendlist(15850593)
			

		