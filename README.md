ost-blogging
-Cody Coats N16282965
============
Blogging App using Goole App Engine


App Contents -------------------------------------------------------------------
--------------------------------------------------------------------------------

css - contains all css files
etc - contains todo.txt but can contain any files not used by app
js - contains all javascript files
static - contains files that do not change
  fonts - glypicons and custom fonts
  images - images that are used by site
templates - all jinja templates store here
  includes - all partials of jinja templates are stored here

ostblogging.py - main app file
helpers.py - addidiotnal files that the app uses

Requirements -------------------------------------------------------------------
--------------------------------------------------------------------------------

1.) The system should handle multiple users and each user should be able to
    create one or more blogs.

    Users are handled by the GAE Users API. Users log in using their google
    account. Users can create multiple blogs from their /home page.
    Blog titles are unique. Two users cannot have the same blog title.

2. A user can select a blog that they own and write a post to that blog.
   A post consists of a title and a body, which will be entered via a CGI form.

   User can select blog from their /home page or go directly to /b/{blog-title}
   to create post. Post titles are unique within a blog. A blog cannot have
   multiple posts with the same title. Post title is limited to 500 characters.
   Post form contains title, tags, and content.
   Post can also be deleted.

3. Blogs can be viewed without an account or login. When viewing a blog, it will
   show at most 10 posts on a page, with a link to go to the next page of older
   posts (you don't need a "newer posts" link).

   An account or login is not requried to view a blog or post. If owner is
   logged in edit/delete buttons appear.
   /b/{blog-title} shows no more than ten posts. These posts are ordered by date
   created not date last-modified. All posts are return from the server.
   The max of ten being displayed is handled by JS. There are prev and next buttons
   to allow users to sort through 'pages' of posts.

4. When multiple posts are shown on the same page(the standard blogview),each
   post will display the content capped at 500 characters. Each post will have a
   "permalink" that, when followed, shows the complete content of the post on
   its own page.

  When a blog is saved (CreatePost/UpdatePost post methods) the full content
  entered is saved as long_content; short_content is capped at 500 characters;
  and orgi_content is the content the user originally typed (this is used so that
  when editing a post the http:// & img replacements are not seen by the user).

  The permalink follows this patter: /p/{blog-tile}/{post-title}.

5. Posts should be stored along with a timestamp when the post was created.
   Posts can be edited, in which case the modification time is stored (and the
   creation time is unchanged); these timestamps will be shown anywhere a post
   is shown. The form presented to a user to edit a post should have the
   original contents (title and body) filled in by default.

   When posts are created two timestamps are created and auto added:
   post.date_created and post.date_modified. date_modified will auto update any
   time a post is saved. The timestamps are displayed using a pretty date filter
   instead of the (ugly) dateime.datetime default.

6. The author of a post can give the post zero or more tags, like "tech" or
   "newyork".

   When creating or editing a post there is an input field to add tags.
   These tags are delimited by " ". The tags input is parsed by the helper
   function parse_tags which returns a list. The list is then saved. When the
   tags are displayed for edit a jinja join filter is used.

7. Posts can be searched for by clicking on a tag, which means only posts with
   the given tag are displayed on the page (again, at most 10 with a link for
   older posts). The list of tags is generated from the set of posts that have
   been stored, and will be displayed on the main page of the blog.

  In the post view if a tag is clicked it will display all posts form all blogs
  with that tag. Users can also search for posts by using the search field in
  the navigation bar by entering a tag.

8. When posts contain links(text that begins with http:// or https://), they
   will be displayed as HTML links when viewed. If a link ends with .jpg, .png,
   or .gif, it will be displayed inline rather than as a link.

  This is handled in two steps. When a post is created or saved the content is
  parsed by the helper function parse_content. Parse content returns all urls
  (regular links or images) inside of an anchor tag. The original content typed
  by the user is saved in orig_content. The long_content contains the output of
  parse_content. short_content does not show links (therefore the blog view does
  not have the links; they are viewed when viewing a post).

  Inline images are displayed using JS. the blog.js The post.js file will find
  all anchor tags which have either an external image ending in an appropriate
  image file extenstion or any blobs(images) saved by users and convert the
  anchor tag into an img tag keeping the href the same.

9. Images can be uploaded. These will be available via a permalink after
   uploaded, and can be referenced using links in the posts.

   Images are uploaded using the /i/new-image link. The images are saved in the
   blobstore.
   To reference in a posted link you must copy the url of the actual image (right click "copy image address").
   This url is listed below the image on the view image page.
   One cannot use /i/{image-title} as that is a link to view the image page not the image.

10. Each blog will have an RSS link, that dumps an entire blog in XML format.

  RSS feeds can be accessed by the /b/{blog-title}/rss link or by clicking the
  "verified RSS" button by the blog title in the blog view. (it is verified RSS :)


Additional features ------------------------------------------------------------
--------------------------------------------------------------------------------
fully styled website lots of pretty CSS
ability to delete posts
newer posts link
Time ago for date_created and date modified
search by tag






