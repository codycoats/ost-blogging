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
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import images

import os, cgi, logging, webapp2, jinja2, math
import helpers

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(
        [os.path.join(os.path.dirname(__file__),"templates/includes"),
         os.path.join(os.path.dirname(__file__),"templates")]),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)
JINJA_ENVIRONMENT.filters['pretty_date'] = helpers.pretty_date

DEFAULT_BLOG_NAME = 'default_blog'
DEFAULT_IMAGE_NAME = 'default_image'
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

class Blog(ndb.Model):
  owner = ndb.UserProperty()
  title = ndb.StringProperty()
  url_title = ndb.StringProperty()

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

    errors = [];

    #create new Blog Model
    blog_name = self.request.get('blog_name',
                                          DEFAULT_BLOG_NAME)
    blog = Blog(parent=blog_key(blog_name))

    if users.get_current_user():
      blog.owner = users.get_current_user()


    blog.title = self.request.get('title')

    ##ensure blog title does not already exist
    check = len(Blog.query(Blog.title == blog.title).fetch())
    print check
    if ( check > 0):
      errors.append("Blog already exists. Please choose a diffferent title.");

      print errors

      template = JINJA_ENVIRONMENT.get_template('new-blog.html')
      template_values = {
        'errors': errors,
        'blog'  : blog
      }
      self.response.write(template.render(template_values))

    else:
      blog.url_title = ("_").join(blog.title.split())

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
      posts = Post.query(Post.blog == blog.title).order(-Post.date_created).fetch()

      num_pages = int(math.ceil(len(posts)/10.0))
      print num_pages

      #render template
      template_values = {
        'found'   : True,
        'blog'    : blog,
        'posts'   : posts,
        'num_pages' : num_pages
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

class RSSBlog(webapp2.RequestHandler):
  def get(self, blog_url_title):
    blog = Blog.query(Blog.url_title == blog_url_title).get()
    posts = Post.query(Post.blog == blog.title).order(-Post.date_created).fetch()

    template_values = {
      'blog' : blog,
      'posts' : posts
    }

    template = JINJA_ENVIRONMENT.get_template('rss.xml')
    self.response.headers["Content-Type"] = 'application/rss+xml'
    self.response.write(template.render(template_values))

class does_not_exist(webapp2.RequestHandler):
  def get(self):
    print "<h1>That page doesn't exist</h1>"
    print "<h2>Sorry :(</h2>"

class Post(ndb.Model):
  author = ndb.UserProperty()
  blog = ndb.StringProperty()
  title = ndb.StringProperty()
  url_title = ndb.StringProperty()
  short_content = ndb.TextProperty()
  long_content = ndb.TextProperty()
  orig_content = ndb.TextProperty()
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
    tags_l = helpers.parse_tags(tags_s)

    orig_content = self.request.get('content')

    #look for webpages & images
    long_content = helpers.parse_content(orig_content)
    short_content = orig_content[:500]

    if long_content != short_content:
      short_content+="..."

    post.tags = tags_l
    post.title = self.request.get('title')
    post.url_title = ("_").join(post.title.split())
    post.long_content = long_content
    post.short_content = short_content
    post.orig_content = orig_content
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

    content = self.request.get('content')
    short_content = content[:500]

    if content != short_content:
      short_content+="..."

    orig_content = self.request.get('content')

    #look for webpages & images
    long_content = helpers.parse_content(orig_content)
    short_content = orig_content[:500]

    #get tags
    tags_s = self.request.get('tags')
    tags_l = helpers.parse_tags(tags_s)

    post.tags = tags_l
    post.title = self.request.get('title')
    post.url_title = ("_").join(post.title.split())
    post.orig_content = orig_content
    post.long_content = long_content
    post.short_content = short_content

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

    posts = Post.query(Post.tags == tag).order(-Post.date_created).fetch()

    template_values = {
      'tag'   : tag,
      'posts' : posts
    }

    template = JINJA_ENVIRONMENT.get_template('tag.html')
    self.response.write(template.render(template_values))

class Image(ndb.Model):
  title = ndb.StringProperty()
  url_title = ndb.StringProperty()
  blob_key = ndb.BlobKeyProperty()
  owner = ndb.UserProperty()
  date_uploaded = ndb.DateTimeProperty(auto_now_add=True)
  caption = ndb.StringProperty()

def image_key(image_name=DEFAULT_IMAGE_NAME):
    """Constructs a Datastore key for a Image entity with image_name."""
    return ndb.Key('Image', image_name)

class NewImage(webapp2.RequestHandler):
  def get(self):
    image_upload_url = blobstore.create_upload_url('/upload-image')

    template_values = {
      'upload_url' : image_upload_url
    }

    template = JINJA_ENVIRONMENT.get_template('upload-image.html')
    self.response.write(template.render(template_values))

class UploadImage(blobstore_handlers.BlobstoreUploadHandler):
  def post(self):
    #create new Blog Model
    image_name = self.request.get('image_name',
                                          DEFAULT_IMAGE_NAME)
    image = Image(parent=image_key(image_name))

    if users.get_current_user():
        image.owner = users.get_current_user()
    else:
      print "<h1> You must be logged in to upload an image.</h1>"
      print "<a href='/home'>Okay :(</a>))"

    uploadedFiles = self.get_uploads()
    blobInfo = uploadedFiles[0]
    image.blob_key = blobInfo.key()
    image.title = self.request.get('title')
    image.url_title = ("_").join(image.title.split())

    #store in DB
    image.put()

    #redirect back to homepage
    self.redirect('/i/'+image.url_title)

class ShowImage(webapp2.RequestHandler):
  def get(self, image_title):
    image = Image.query(Image.url_title == image_title).fetch()[0]

    print image.blob_key

    template_values = {
      'image' : image,
      'img_url' : images.get_serving_url(image.blob_key)
    }

    print template_values['img_url']

    template = JINJA_ENVIRONMENT.get_template('image.html')
    self.response.write(template.render(template_values))


# class ShowImage(webapp2.RequestHandler):
#   def get(self,imageid):

app = webapp2.WSGIApplication([
  ('/', MainHandler),
  ('/home', UserHome),
  ('/b/new-blog', NewBlog),
  ('/b/create-blog', CreateBlog),
  #(r'/b/(.*)/edit-blog', EditBlog),
  #('r/b/(.*)/update-blog(.*), UpdateBlog'),
  #('r/b/(.*)/delete-blog(.*), DeleteBlog'),
  #('r/b/(.*)/destroy-blog(.*), DestroyBlog'),
  (r'/b/(.*)/rss', RSSBlog),
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
  ('/i/new-image', NewImage),
  ('/upload-image', UploadImage),
  (r'/i/(.*)', ShowImage),
  (r'/(.*)', does_not_exist)
], debug=True)
