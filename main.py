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
import cgi
from google.appengine.ext import db

import jinja2
import webapp2
from google.appengine.api import urlfetch
import urllib

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)


class MainHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self,template, **kw):
        self.write(self.render_str(template, **kw))

class Posting(db.Model):
    title = db.StringProperty(required = True)
    blog = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

def get_posts(limit,offset):
    limit = int(limit)
    offset= int(offset)
    blogs = db.GqlQuery("SELECT * FROM Posting "
                        "ORDER BY created DESC "
                        "LIMIT {limit} OFFSET {offset}".format(limit=limit, offset=offset))
    return blogs

class MainPage(MainHandler):
    def render_front(self, title="", blog="", gp="", prev_url="", prev=""):
        # blogs = db.GqlQuery("SELECT * FROM Posting "
        #                     "ORDER BY created DESC "
        #                    "LIMIT 5 ")

        self.render("front.html", title=title, blog=blog, gp=gp, prev_url=prev_url, prev=prev)

    def get(self):

        page = int(self.request.GET['page'])
        limit = 5
        offset = (page - 1) * limit

        count = Posting.all().count()
        gp = get_posts(limit, offset)
        # prev = str(page - 1)
        # prev = offset - limit
        # prev_url = "http://localhost:9080/blog?page={0}".format(prev)
        prev = str(page - 1)
        prev_url = "/blog?page=" + prev
        if page > count / limit:
            self.error(404)
        else:
            self.response.write(prev_url)
            self.render_front(gp = gp, prev_url=prev_url, prev=prev)

class NewPost(MainHandler):
    def render_newpost(self, title="", blog="", error=""):
        self.render("newpost.html", title=title, blog=blog, error=error)

    def get(self):
        self.render_newpost()

    def post(self):
        title = self.request.get('title')
        blog = self.request.get('blog')

        if title and blog:
            a = Posting(title=title, blog=blog)
            a.put()
            self.redirect("/blog/%s" % a.key().id())
        else:
            error = "Please submit both a title and a blog post!"
            self.render_newpost(title, blog, error)

class ViewPostHandler(webapp2.RequestHandler):
    # def render_plnk(self, title="", blog="", p=""):
    #     self.render("plink.html", title=title, blog=blog, p=p)

    def get(self, id):
        p = Posting.get_by_id(int(id))
        t = jinja_env.get_template("plnk.html")
        content = t.render(p=p)
        self.response.write(content)


app = webapp2.WSGIApplication([
    ('/blog', MainPage),
    ('/newpost', NewPost),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
