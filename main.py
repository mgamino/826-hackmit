import webapp2
import jinja2
import os
from google.appengine.ext import ndb
import logging

class Profile (ndb.Model):
    name = ndb.StringProperty()
    bio = ndb.TextProperty()
    accountCreated = ndb.DateTimeProperty(auto_now_add=True)

class Story (ndb.Model):
	title = ndb.StringProperty()
	# author = fuck
	# publicationDate = fuck
	writtenDate = ndb.DateTimeProperty(auto_now_add=True)
	prompt = ndb.TextProperty()
	visualTheme = ndb.StringProperty()
	structure = ndb.StringProperty()
	published = ndb.BooleanProperty()

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_environment = jinja2.Environment(
  loader=jinja2.FileSystemLoader(template_dir))

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
