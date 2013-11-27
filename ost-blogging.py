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
from google.appengine.api import users
from google.appengine.ext import ndb

import os, cgi, logging, webapp2, jinja2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class MainHandler(webapp2.RequestHandler):

  def get(self):
    #if user is logged in redirect to their home page
    user = users.get_current_user()

    if user:
      self.redirect('/home')
    else:
      #else render splash page
      template_values = {
        'blog_title': "Splash"
      }

      template = JINJA_ENVIRONMENT.get_template('index.html')
      self.response.write(template.render(template_values));

class UserHome(webapp2.RequestHandler):

  def get(self):
    #get user's list of blogs
    user = users.get_current_user()
    logging.debug("current user: %s", str(user))
    user_blogs = Blog.query(Blog.owner == user)
    logging.debug("%s's blogs: %s", str(user), str(user_blogs))

    logging.debug(type(user_blogs))

    template_values = {
      'user'  : user,
      'blogs' : user_blogs
    }

    template = JINJA_ENVIRONMENT.get_template('home.html')
    self.response.write(template.render(template_values));


#Models
class Post(ndb.Model):
  author = ndb.UserProperty()
  content = ndb.TextProperty()
  date = ndb.DateTimeProperty(auto_now_add=True)

class Blog(ndb.Model):
  owner = ndb.UserProperty()
  title = ndb.StringProperty()
  posts = ndb.StructuredProperty(Post, repeated=True)



app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/home', UserHome)
], debug=True)
