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
# import urllib
#
# from google.appengine.api import users
from google.appengine.ext import db

import jinja2
import webapp2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class MainHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.write(*a, **kw)

    def render_str(self, template, **params):
        t = JINJA_ENVIRONMENT.get_template(template)
        return t.render(params)

    def render(self,template, **kw):
        self.write(self.render_str(template, **kw))

class Blog(db.Model):
    title = db.StringProperty(required = True)
    blog = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class MainPage(MainHandler):
    def render_front(self, title="", blog="",error=""):
        blogs = db.GqlQuery("SELECT * FROM Blog "
                            "ORDER BY created DESC ")

        self.render("front.html", title=title, blog=blog, error=error, blogs=blogs)

    def get(self):
        self.render_front()

    def post(self):
        title = self.request.get('title')
        blog = self.request.get('blog')

        if title and blog:
            a = Blog(title=title, blog=blog)
            a.put()

            self.redirect("/")
        else:
            error = "We need both a title and a blog post!"
            self.render_front(title, blog, error)

app = webapp2.WSGIApplication([
    ('/', MainPage)
], debug=True)
