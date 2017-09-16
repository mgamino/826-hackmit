import webapp2
import jinja2
import os
from google.appengine.ext import ndb
import logging

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('Hello world!')

class ProfileHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('Hello world!')

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/profile', ProfileHandler),
], debug=True)
