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

from string import maketrans
import os, cgi, logging, webapp2, jinja2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

DEFAULT_BLOG_NAME = 'default_blog'
DEFAULT_POST_NAME = 'default_post'

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
    if users.get_current_user():
      template = JINJA_ENVIRONMENT.get_template('new-blog.html')
      self.response.write(template.render())
    else:
      template = JINJA_ENVIRONMENT.get_template('must-login.html')
      template_values = { 'reason': 'Create a New Blog'}
      self.response.write(template.render(template_values))

class CreateBlog(webapp2.RequestHandler):
  def post(self):
    #create new Blog Model
    blog_name = self.request.get('blog_name',
                                          DEFAULT_BLOG_NAME)
    blog = Blog(parent=blog_key(blog_name))

    if users.get_current_user():
        blog.owner = users.get_current_user()

    blog.title = self.request.get('title')
    blog.url_title = ("_").join(blog.title.split())

    logging.debug(blog.url_title)

    #store in DB
    blog.put()

    #redirect back to homepage
    self.redirect('/home')
  def get(self):
    self.redirect('/doesnotexist')

class ShowBlog(webapp2.RequestHandler):
  def get(self, blog_url_title):
    #get current blog
    blog = Blog.query(Blog.url_title == blog_url_title).get()

    ##If blog doesn't exist redirect
    if (blog):
      #get all posts of blog
      logging.debug(blog);
      blog_posts_query = Post.query(Post.blog == blog.title)
      blog_posts_query.order(Post.date_created)
      posts = blog_posts_query.fetch(limit=10)

      #render template
      template_values = {
        'found'   : True,
        'blog'    : blog,
        'posts'   : posts
      }

      ##check if owner is viewing
      if (users.get_current_user() == blog.owner):
        template_values['user'] = 'owner'
      else:
        template_values['user'] = 'visitor'

    else:
      logging.debug("Blog not found");
      template_values = {
          'found': False
      }

    template = JINJA_ENVIRONMENT.get_template('blog.html')
    self.response.write(template.render(template_values))

def post_key(post_name=DEFAULT_POST_NAME):
    """Constructs a Datastore key for a Post entity with post_name."""
    return ndb.Key('Post', post_name)

class NewPost(webapp2.RequestHandler):
  def get(self, blog_url_title):

    blog = Blog.query(Blog.url_title == blog_url_title).get()

    template_values = {
      'blog' : blog
    }

    template = JINJA_ENVIRONMENT.get_template('new-post.html')
    self.response.write(template.render(template_values))

class CreatePost(webapp2.RequestHandler):
  def post(self, blog_url_title):
    #create new Blog Model
    post_name = self.request.get('post_name',
                                          DEFAULT_POST_NAME)
    post = Post(parent=post_key(post_name))

    if users.get_current_user():
        post.author = users.get_current_user()
    else:
      print "<h1> You must be logged in to create a post.</h1>"
      print "<a href='/home'>Okay :(</a>))"

    post.title = self.request.get('title')
    post.url_title = ("_").join(post.title.split())
    post.content = self.request.get('content')
    post.blog = Blog.query(Blog.url_title == blog_url_title).get().title

    #store in DB
    post.put()

    #redirect back to homepage
    self.redirect('/b/'+blog_url_title)

class ShowPost(webapp2.RequestHandler):
  def get(self, blog_url_title, post_url_title):
    blog = Blog.query(Blog.url_title == blog_url_title).get()
    post = Post.query(Post.blog == blog.title, Post.url_title == post_url_title).get()

    logging.debug("Post found is: "+str(post))

    template_values = {
      'blog' : blog,
      'post' : post
    }

    template = JINJA_ENVIRONMENT.get_template('post.html')
    self.response.write(template.render(template_values))



class does_not_exist(webapp2.RequestHandler):
  def get(self):
    print "<h1>That page doesn't exist</h1>"
    print "<h2>Sorry :(</h2>"

#Models
#
#
class Blog(ndb.Model):
  owner = ndb.UserProperty()
  title = ndb.StringProperty()
  url_title = ndb.StringProperty()

class Post(ndb.Model):
  author = ndb.UserProperty()
  blog = ndb.StringProperty()
  title = ndb.StringProperty()
  url_title = ndb.StringProperty()
  content = ndb.TextProperty()
  date_created = ndb.DateTimeProperty(auto_now_add=True)
  date_last_modified = ndb.DateTimeProperty(auto_now_add=True)
  tags = ndb.StringProperty(repeated=True)

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/home', UserHome),
    ('/b/new-blog', NewBlog),
    ('/b/create-blog', CreateBlog),
    #(r'/b/(.*)/edit-blog', EditBlog),
    #('r/b/(.*)/update-blog(.*), UpdateBlog'),
    #('r/b/(.*)/delete-blog(.*), DeleteBlog'),
    #('r/b/(.*)/destroy-blog(.*), DestroyBlog'),
    (r'/b/(.*)', ShowBlog),
    (r'/p/(.*)/new-post', NewPost),
    (r'/p/(.*)/create-post', CreatePost),
    #(r'/p/(.*)/edit-post', EditBlog),
    #('r/p/(.*)/update-post(.*), UpdatePost'),
    #('r/p/(.*)/delete-post(.*), DeletePost'),
    #('r/p/(.*)/destroy-post(.*), DestroyPost'),
    (r'/p/(.*)/(.*)', ShowPost),
    (r'/(.*)', does_not_exist)
], debug=True)
