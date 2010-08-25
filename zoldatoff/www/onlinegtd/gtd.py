#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import cgi
import os

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template

from google.appengine.ext import db

from google.appengine.api import users

from django.utils import simplejson

##########################################################################################################


# Exception on inserting not unique value
class UniqueConstraintViolation(Exception):
	def __init__(self, scope, value):
		super(UniqueConstraintViolation, self).__init__("Value '%s' is not unique within scope '%s'." % (value, scope))
		
##########################################################################################################

class GtdObject(db.Model):
	user = db.UserProperty()
	name = db.StringProperty(required=True)
	change_date = db.DateTimeProperty(auto_now_add=True)
		
	def text(self):
		return 'key = ' + str(self.key().id()) + \
				' name = ' + self.name + \
				' user = ' + str(self.user) + \
				' change_date = ' + str(self.change_date)
	
	def json(self):
		return dict(id=self.key().id(), name=self.name)

class GtdUniqueObject(GtdObject):
	def put(self):
		if GtdUniqueObject.gql("WHERE user=:user AND name=:name", user=self.user, name=self.name).count():
			raise UniqueConstraintViolation("name", self.name)
        	
		#self._key_name = self.name
		return db.Model.put(self)


# Context
class Context(GtdUniqueObject): pass
	
# Folder
class Folder(GtdUniqueObject): pass
	
# Project
class Project(GtdObject): pass
	
# Project
class Task(GtdObject): pass
	
##########################################################################################################

class GtdObjectHandler(webapp.RequestHandler):
	
	def __init__(self, gtdobjname):
		self.Gobject = gtdobjname #globals().get(gtdobjname)
		super(GtdObjectHandler, self).__init__()

	def get(self):
			
		action = self.request.get('action')
		
		if action == 'list':
			gtdobjects = self.Gobject.gql("WHERE user = :user ORDER BY change_date", user=users.get_current_user())
			result = []
			
			for gtdobject in gtdobjects:
				result.append(gtdobject.json())
				
			self.response.out.write(simplejson.dumps(result))
				
		elif action == 'create':
			gtdobject = self.Gobject(name=self.request.get('name'))
			gtdobject.user = users.get_current_user()
			gtdobject.put()
			
			self.response.out.write(simplejson.dumps(gtdobject.json()))
			
		elif action == 'delete':
			gtdobject = self.Gobject.get_by_id(self.request.get('id'))
			self.response.out.write(simplejson.dumps(gtdobject.json()))
			gtdobject.delete()
			
		elif action == 'rename':
			gtdobject = self.Gobject.get_by_id(self.request.get('id'))
			gtdobject.name = self.request.get('name')
			gtdobject.put()
			self.response.out.write(simplejson.dumps(gtdobject.json()))
		
		else:
			self.response.out.write('Nothing happened')

# Context web request hander	
class ContextHandler(GtdObjectHandler):
	def __init__(self):
		super(ContextHandler, self).__init__(Context)

class FolderHandler(GtdObjectHandler):
	def __init__(self):
		super(FolderHandler, self).__init__(Folder)
			
##########################################################################################################

class MainHandler(webapp.RequestHandler):
	def get(self):		
		if users.get_current_user():
			None
		else:
			self.redirect(users.create_login_url(self.request.uri))
			
			
def main():
    application = webapp.WSGIApplication([('/a/', MainHandler),
    									  ('/a/context', ContextHandler),
    									  ('/a/folder', FolderHandler)
    									],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()