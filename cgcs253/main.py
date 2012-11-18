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
import os
import webapp2
import jinja2

from google.appengine.ext import db


template_dir = os.path.join(os.path.dirname(__file__), 'templates') # __file__ is *this* file
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)


class BaseRedirect(webapp2.RequestHandler):
    """Redirect to blog homepage"""
    def get(self):
        self.redirect('/blog')


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        """Helper function for render()"""
        self.response.write(*a, **kw)

    def render_str(self, template, **params):
        """Helper function for render()"""
        jinja_template = jinja_env.get_template(template)
        return jinja_template.render(params)

    def render(self, template, **kw):
        """Helper function exposed to dependent classes"""
        self.write(self.render_str(template,**kw))


class MainPage(Handler):
    """Basic landing page"""
    def get(self):
        posts_from_db = db.GqlQuery("SELECT * FROM BlogPosts ORDER BY created   DESC")
        self.render("main.html",posts=posts_from_db,linkBack="")


class NewPost(Handler):
    """Add a new post to the blog"""
    def get(self,subject="",content="",error=""):
        self.render("form.html",subject=subject,content=content,error=error)
    
    def post(self):
        subject = self.request.get('subject')
        content = self.request.get('content')

        if subject and content:
            bp = BlogPosts(subject=subject,content=content)
            post_key = bp.put()
        
            self.redirect('/blog/%d' % int(post_key.id()))
        else:
            if not subject and not content:
                error_msg = "You need both a subject and content."
            elif not subject:
                error_msg = "You need a valid subject."
            elif not content:
                error_msg = "You need valid contents."
            self.get(subject=subject,content=content,error=error_msg)


class Permalink(Handler):
    def get(self,id):
        self.render("main.html",
                    posts=[BlogPosts.get_by_id(int(id))],
                    linkBack="Home")


class BlogPosts(db.Model):
    """Create datastore with subject, content, and created date."""
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)


app = webapp2.WSGIApplication([
    ('/', BaseRedirect),
    ('/blog', MainPage),
    ('/blog/newpost', NewPost),
    ('/blog/(\d+)', Permalink)
], debug=True)
