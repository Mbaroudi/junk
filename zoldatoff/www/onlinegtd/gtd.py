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


# Exception on inserting not unique value
class UniqueConstraintViolation(Exception):
	def __init__(self, scope, value):
		super(UniqueConstraintViolation, self).__init__("Value '%s' is not unique within scope '%s'." % (value, scope))

# Context
class Context(db.Model):
	user = db.UserProperty()
	name = db.StringProperty(required=True)
	change_date = db.DateTimeProperty(auto_now_add=True)
	
	def put(self):
		if Context.gql("WHERE user=:user AND name=:name", user=self.user, name=self.name).count():
			raise UniqueConstraintViolation("name", self.name)
        	
		#self._key_name = self.name
		return db.Model.put(self)
		
	def text(self):
		print 'key = ' + str(self.key().id()) + \
				' name = ' + self.name + \
				' user = ' + str(self.user) + \
				' change_date = ' + str(self.change_date)
	
	def json(self):
		return dict(id=self.key().id(), name=self.name)

# Context web request hander	
class ContextHandler(webapp.RequestHandler):
	def get(self):
	
		print 'Content-Type: text/plain'
		print ''
			
		action = self.request.get('action')
		
		if action == 'get':
			contexts = Context.gql("WHERE user = :user ORDER BY change_date", user=users.get_current_user())
			result = []
			
			for context in contexts:
				result.append(context.json())
				
			self.response.out.write(simplejson.dumps(result))
				
		elif action == 'create':
			context = Context(name=self.request.get('name'))
			context.user = users.get_current_user()
			context.put()
			print 'Created context: ' + context.text()
		
		else:
			print 'Nothing happened'
			


class MainHandler(webapp.RequestHandler):
	def get(self):
		user = users.get_current_user()
		
		if user:
			path = os.path.join(os.path.dirname(__file__), 'index.html')
			self.response.out.write(template.render(path, None))
		else:
			self.redirect(users.create_login_url(self.request.uri))
			
			
def main():
    application = webapp.WSGIApplication([('/a/', MainHandler),
    									  ('/a/context', ContextHandler)
    									],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()