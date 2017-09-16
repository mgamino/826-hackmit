import webapp2
import jinja2
import os
from google.appengine.api import users
from google.appengine.ext import ndb
import logging

#TODO: finish figuring out the profile bullshit lmao


class Profile (ndb.Model):
    name = ndb.StringProperty()
    bio = ndb.TextProperty()
    accountCreated = ndb.DateTimeProperty(auto_now_add=True)

class Story (ndb.Model):
	title = ndb.StringProperty()
	profile_email = ndb.StringProperty()
	publicationDate = ndb.DateTimeProperty()
	writtenDate = ndb.DateTimeProperty(auto_now_add=True)
	prompt = ndb.TextProperty()
	visualTheme = ndb.StringProperty()
	structure = ndb.StringProperty()
	views = ndb.IntegerProperty()
	published = ndb.BooleanProperty()

class StoryCard(ndb.Model):
    text = ndb.TextProperty()
    story_key = ndb.KeyProperty(kind = Story)
    cardNumber = ndb.StringProperty()

class Submission(ndb.Model):
	text = ndb.TextProperty()
	profile_email = ndb.StringProperty()

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))

class MainHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()

        if user:
            email = user.email().lower()
            logout_url=users.CreateLogoutURL('/')

            #TODO: if profile w/ matching email does not exist, create profile object with name, bio, and others set as some boring defaults (think uber driver profiles)

            template_vals = {'email':email, 'logout_url':logout_url}
            template = jinja_environment.get_template("main.html")
            self.response.write(template.render(template_vals))
        else:
            login_url = users.CreateLoginURL('/')
            template = jinja_environment.get_template("login.html")
            self.response.write(template.render())

class ProfileHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        user_email = user.email()
        #TODO: query for profile key with this email
        logout_url=users.CreateLogoutURL('/')

        #TODO: query stories for user key (email?) is this one!
        #TODO: actually do that twice, once for published and one not published
        #TODO: jk make it 3, one for published, one for finished not published (awaiting approval), and one for in progress (so u can get the story key from URL)


        template = jinja_environment.get_template("profile.html")
        template_vals = {'logout_url':logout_url}
        self.response.write(template.render(template_vals))

class SetProfileHandler(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template("setprofile.html")
        self.response.write(template.render())

    #TODO: def post(self) with fields

class ReadHandler(webapp2.RequestHandler):
    def get(self):
        #TODO: query stories where published == true
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

	def post(self):
		title = self.request.get('title')
		profile = users.get_current_user()
		profile_email = profile.email.lower()
		prompt = self.request.get('prompt')
		visualTheme = self.request.get('visualTheme')
		structure = self.request.get('structure')

		story = Story(text = text, profile_email = profile_email, prompt = prompt, visualTheme = visualTheme, structure = structure, views = 0, published = False)
		story.put()
		if structure == "freewrite":
			self.redirect('/freewrite')
		else:
			self.redirect('/cyoa')

class FreewriteHandler(webapp2.RequestHandler):
    def get(self):
        #TODO: something about loading the story key?? from url maybe??
        template = jinja_environment.get_template("freewrite.html")
        self.response.write(template.render())
    #TODO: def post(self): save the card & story

	def post(self):
		text = self.request.get('text')
		story_key = "shit"

		storycard = StoryCard(text = text, story_key = story_key, cardNumber = "1")
		storycard.put()
		self.redirect("/profile")

class CyoaHandler(webapp2.RequestHandler):
    def get(self):
        #TODO: template_vals for user + story_key
        template = jinja_environment.get_template("cyoa.html")
        self.response.write(template.render())
    def post(self):
        one = self.request.get("one")
        one_one = self.request.get("one_one")
        one_one_one = self.request.get("one_one_one")

        one_one_two = self.request.get("one_one_two")

        one_two = self.request.get("one_two")
        one_two_one = self.request.get("one_two_one")

        one_two_two = self.request.get("one_two_two")

        two = self.request.get("two")
        two_one = self.request.get("two_one")
        two_two = self.request.get("two_two")

        #TODO(megan): card.put!! for all of these also get story keY>??


class SubmitHandler(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template("submit.html")
        self.response.write(template.render())

	def post(self):
		text = self.request.get('text')
		profile = users.get_current_user()
		profile_email = profile.email().lower()

		submission = Submission(text = text, profile_email = profile_email)
		submission.put()
		self.redirect("/submitted")

class SubmittedHandler(webapp2.RequestHandler):
	def get(self):
		template = jinja_environment.get_template("submitted.html")
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
    ('/cyoa', CyoaHandler),
    ('/submit', SubmitHandler),
	('/submitted',SubmittedHandler)
], debug=True)
