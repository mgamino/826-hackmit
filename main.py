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
	profile_key = ndb.KeyProperty(kind = Profile)
	publicationDate = ndb.DateTimeProperty()
	writtenDate = ndb.DateTimeProperty(auto_now_add=True)
	prompt = ndb.TextProperty()
	visualTheme = ndb.StringProperty()
	structure = ndb.StringProperty()
	published = ndb.BooleanProperty()

class StoryCard(ndb.Model):
    text = ndb.TextProperty()
    story_key = ndb.KeyProperty(kind = Story)
    cardNumber = ndb.StringProperty()

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_environment = jinja2.Environment(
  loader=jinja2.FileSystemLoader(template_dir))

class MainHandler(webapp2.RequestHandler):
    def get(self):
    	template = jinja_environment.get_template("main.html")
		self.response.write(template.render())

class ProfileHandler(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template("profile.html")
		self.response.write(template.render())

class SetProfileHandler(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template("setprofile.html")
		self.response.write(template.render())

class ReadHandler(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template("read.html")
		self.response.write(template.render())

class ReadCyoaHandler(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template("readcyoa.html")
        self.response.write(template.render())

class ReadFreewriteHandler(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template("readfreewrite.html")
        self.response.write(template.render())

class WriteHandler(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template("write.html")
		self.response.write(template.render())

class FreewriteHandler(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template("freewrite.html")
        self.response.write(template.render())

class CyoaHandler(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template("cyoa.html")
        self.response.write(template.render())

class SubmitHandler(webapp2.RequestHandler):
	def get(self):
		template = jinja_environment.get_template("submit.html")
		self.response.write(template.render())

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/profile', ProfileHandler),
    ('/setprofile', SetProfileHandler),
    ('/read', ReadHandler),
	('/readcyoa',ReadCyoaHandler),
    ('/readfreewrite',ReadFreewriteHandler),
    ('/write',WriteHandler),
	('/freewrite',FreewriteHandler),
	('/editfreewrite',EditFreewriteHandler),
	('/cyoa', CyoaHandler),
    ('/submit', SubmitHandler),
], debug=True)
