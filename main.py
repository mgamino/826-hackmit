import webapp2
import jinja2
import os
from google.appengine.ext import ndb
import logging

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('Main page')

class ProfileHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('Profile Page')

class ReadHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('Read page')

class WriteHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('Write Page')

class SubmitHandler(webapp2.RequestHandler):
	def get(self):
		self.response.write('Submit page')

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/profile', ProfileHandler),
    ('/read', ReadHandler),
    ('/write',WriteHandler),
    ('/submit', SubmitHandler),
], debug=True)
