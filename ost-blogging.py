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

DEFAULT_BLOG_NAME = 'default_blog'


class MainHandler(webapp2.RequestHandler):

  def get(self):
    #if user is logged in redirect to their home page
    user = users.get_current_user()

    if user:
      self.redirect('/home')
    else:
      #else render splash page

      url = users.create_login_url(self.request.uri)
      url_linktext = 'Login'

      template_values = {
        'url'          : url,
        'url_linktext' : url_linktext
      }

      template = JINJA_ENVIRONMENT.get_template('index.html')
      self.response.write(template.render(template_values));

class UserHome(webapp2.RequestHandler):
  def get(self):
    if users.get_current_user():
      user = users.get_current_user()

      logging.debug("current user: %s", str(user))
      user_blogs_query = Blog.query(Blog.owner == user)
      user_blogs = user_blogs_query.fetch()

      logging.debug("%s's blogs: %s", user, user_blogs)

      url = users.create_logout_url(self.request.uri)
      url_linktext = 'Logout'

      logging.debug(url, url_linktext)

      template_values = {
        'user'    : user,
        'blogs'   : user_blogs,
        'url'     : url,
        'url_linktext': url_linktext
      }

      template = JINJA_ENVIRONMENT.get_template('home.html')
      self.response.write(template.render(template_values))

    else:
      self.redirect('/')

def blog_key(blog_name=DEFAULT_BLOG_NAME):
    """Constructs a Datastore key for a Blog entity with blog_name."""
    return ndb.Key('Blog', blog_name)

class NewBlog(webapp2.RequestHandler):
  def get(self):
    template = JINJA_ENVIRONMENT.get_template('new-blog.html')
    self.response.write(template.render())

class CreateBlog(webapp2.RequestHandler):
  def post(self):
    #create new Blog Model
    blog_name = self.request.get('blog_name',
                                          DEFAULT_BLOG_NAME)
    blog = Blog(parent=blog_key(blog_name))

    if users.get_current_user():
        blog.owner = users.get_current_user()

    blog.title = self.request.get('title')

    #store in DB
    blog.put()

    #redirect back to homepage
    self.redirect('/home')





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
    ('/home', UserHome),
    ('/new-blog', NewBlog),
    ('/create-blog', CreateBlog),
], debug=True)
