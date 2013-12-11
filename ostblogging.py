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
from helpers import parse_tags

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
      posts = Post.query(Post.blog == blog.title).order(-Post.date_created).fetch(10)

      #render template
      template_values = {
        'found'   : True,
        'blog'    : blog,
        'posts'   : posts,
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

class does_not_exist(webapp2.RequestHandler):
  def get(self):
    print "<h1>That page doesn't exist</h1>"
    print "<h2>Sorry :(</h2>"

def pretty_date(time=False):
    """
    Get a datetime object or a int() Epoch timestamp and return a
    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
    'just now', etc
    """
    from datetime import datetime
    now = datetime.now()
    if type(time) is int:
        diff = now - datetime.fromtimestamp(time)
    elif isinstance(time,datetime):
        diff = now - time
    elif not time:
        diff = now - now
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ''

    if day_diff == 0:
        if second_diff < 10:
            return "just now"
        if second_diff < 60:
            return str(second_diff) + " seconds ago"
        if second_diff < 120:
            return  "a minute ago"
        if second_diff < 3600:
            return str( second_diff / 60 ) + " minutes ago"
        if second_diff < 7200:
            return "an hour ago"
        if second_diff < 86400:
            return str( second_diff / 3600 ) + " hours ago"
    if day_diff == 1:
        return "Yesterday"
    if day_diff < 7:
        return str(day_diff) + " days ago"
    if day_diff < 31:
        return str(day_diff/7) + " weeks ago"
    if day_diff < 365:
        return str(day_diff/30) + " months ago"
    return str(day_diff/365) + " years ago"


def format_number(number):
    s = '%d' % number
    groups = []
    while s and s[-1].isdigit():
        groups.append(s[-3:])
        s = s[:-3]
    return s + ','.join(reversed(groups))

JINJA_ENVIRONMENT.filters['pretty_date'] = pretty_date


DEFAULT_POST_NAME = 'default_post'

class Post(ndb.Model):
  author = ndb.UserProperty()
  blog = ndb.StringProperty()
  title = ndb.StringProperty()
  url_title = ndb.StringProperty()
  content = ndb.TextProperty()
  date_created = ndb.DateTimeProperty(auto_now_add=True)
  date_last_modified = ndb.DateTimeProperty(auto_now=True)
  tags = ndb.StringProperty(repeated=True)

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

    #get tags
    tags_s = self.request.get('tags')
    tags_l = parse_tags(tags_s)

    post.tags = tags_l
    print(len(post.tags))
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
    blog = Blog.query(blog_url_title == Blog.url_title).get()
    post = Post.query(blog.title == Post.blog, post_url_title == Post.url_title).get()

    logging.debug("Post found is: "+str(post))

    print(len(post.tags))

    template_values = {
      'blog' : blog,
      'post' : post,
    }

    template = JINJA_ENVIRONMENT.get_template('post.html')
    self.response.write(template.render(template_values))

class EditPost(webapp2.RequestHandler):
  def get(self, blog_url_title, post_url_title):

    print(blog_url_title)
    print(post_url_title)

    blog = Blog.query(blog_url_title == Blog.url_title).get()
    post = Post.query(blog.title == Post.blog, post_url_title == Post.url_title).get()

    print(post.url_title == post_url_title)

    template_values = {
      'blog' : blog,
      'post' : post
    }

    template = JINJA_ENVIRONMENT.get_template('edit-post.html')
    self.response.write(template.render(template_values))

class UpdatePost(webapp2.RequestHandler):
  def post(self, blog_url_title, post_url_title):

    blog = Blog.query(blog_url_title == Blog.url_title).get()
    post = Post.query(blog.title == Post.blog, post_url_title == Post.url_title).get()

    if not (users.get_current_user() == post.author):
      print "<h1> You must be logged and be the owner of the post to update it.</h1>"
      print "<a href='/home'>Okay :(</a>))"

    post.title = self.request.get('title')
    post.url_title = ("_").join(post.title.split())
    post.content = self.request.get('content')

    #store in DB
    post.put()

    #redirect back to homepage
    self.redirect('/p/'+blog_url_title+'/'+post.url_title)

class DeletePost(webapp2.RequestHandler):
  def get(self, blog_url_title, post_url_title):
    blog = Blog.query(blog_url_title == Blog.url_title).get()
    post = Post.query(blog.title == Post.blog, post_url_title == Post.url_title).get()

    template_values = {
      'blog' : blog,
      'post' : post
    }

    template = JINJA_ENVIRONMENT.get_template('delete-post.html')
    self.response.write(template.render(template_values))

class DestroyPost(webapp2.RequestHandler):
  def post(self, blog_url_title, post_url_title):

    blog = Blog.query(blog_url_title == Blog.url_title).get()
    post = Post.query(blog.title == Post.blog, post_url_title == Post.url_title).get()

    if not (users.get_current_user() == post.author):
      print "<h1> You must be logged and be the owner of the post to delete it.</h1>"
      print "<a href='/home'>Okay :(</a>))"

    #store in DB
    post.key.delete()

    #redirect back to homepage
    self.redirect('/b/'+blog_url_title)

class SearchTag(webapp2.RequestHandler):
  def get(self, tag):
    if tag == "":
      tag = self.request.get('tag')

    posts = Post.query(Post.tags == tag)

    template_values = {
      'tag'   : tag,
      'posts' : posts
    }

    template = JINJA_ENVIRONMENT.get_template('tag.html')
    self.response.write(template.render(template_values))

class Blog(ndb.Model):
  owner = ndb.UserProperty()
  title = ndb.StringProperty()
  url_title = ndb.StringProperty()

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
    (r'/p/(.*)/(.*)/edit-post', EditPost),
    (r'/p/(.*)/(.*)/update-post', UpdatePost),
    (r'/p/(.*)/(.*)/delete-post', DeletePost),
    (r'/p/(.*)/(.*)/destroy-post', DestroyPost),
    (r'/p/(.*)/(.*)', ShowPost),
    (r'/t/?(.*)', SearchTag),
    (r'/t/(.*)', SearchTag),
    (r'/(.*)', does_not_exist)
], debug=True)