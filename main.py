import webapp2
import jinja2
import os
from google.appengine.api import users
from google.appengine.ext import ndb
import logging
import smtplib




class Profile (ndb.Model):
    name = ndb.StringProperty()
    bio = ndb.TextProperty()
    accountCreated = ndb.DateTimeProperty(auto_now_add=True)
    email = ndb.StringProperty()

class Story (ndb.Model):
	title = ndb.StringProperty()
	profile_key = ndb.KeyProperty(kind = Profile)
	publicationDate = ndb.DateTimeProperty()
	writtenDate = ndb.DateTimeProperty(auto_now_add=True)
	prompt = ndb.TextProperty()
	visualTheme = ndb.StringProperty()
	structure = ndb.StringProperty()
	views = ndb.IntegerProperty()
	published = ndb.BooleanProperty()
    submitted = ndb.BooleanProperty()

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

            user = Profile.query(profile.email == email).fetch()
            if (len(user)) <1):
                profile = Profile(name = "Amazing Author", bio = "I love storytelling!", email = email)
                profile.put()

            profile = Profile.query(profile.email == email).fetch()

            template_vals = {'profile':profile, 'logout_url':logout_url}
            template = jinja_environment.get_template("main.html")
            self.response.write(template.render(template_vals))
        else:
            login_url = users.CreateLoginURL('/')
            template = jinja_environment.get_template("login.html")
            self.response.write(template.render())

class ProfileHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        email = user.email()

        urlsafe_key = self.request.get('key')
        key = ndb.Key(urlsafe = urlsafe_key)

        profile = Profile.query()
        logout_url=users.CreateLogoutURL('/')

        publishedStories = Story.query(Story.profile_key == profile.key, Story.published == True)
        inProgressStories = Story.query(Story.profile_key == profile.key, Story.published==False, Story.submitted == True).fetch()
        draftStories = Story.query(Story.profile_key==profile.key, Story.submitted==False).fetch()

        template_vals = {'profile':profile, 'logout_url':logout_url, 'publishedStories':publishedStories, 'inProgressStories':inProgressStories, 'draftStories':draftStories}

        template = jinja_environment.get_template("profile.html")
        template_vals = {'publishedStories':publishedStories, 'inProgressStories': inProgressStories, 'draftStories':draftStories, 'logout_url':logout_url}
        self.response.write(template.render(template_vals))

class SetProfileHandler(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template("setprofile.html")
        self.response.write(template.render())

    def post(self):
		urlsafekey = self.request.get('key')
        key = ndb.Key(urlsafe = urlsafekey)
        profile = key.get()

        name = self.request.get('name')
		if name == "":
			name = profile.name
		else:
			profile.name = name;
			profile.put()

        bio = self.request.get('bio')
		if bio == "":
			bio = profile.bio
		else:
			profile.bio = bio;
			profile.put()

        user = users.get_current_user()
        email = user.email().lower()

        profile = Profile(name = name, bio = bio, email = email)

        profile.put()

        self.redirect('/profile')

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

		story = Story(text = text, profile_email = profile_email, prompt = prompt, visualTheme = visualTheme, structure = structure, views = 0, published = False, approved = False)
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
        urlsafekey = self.request.get('key')
        key = ndb.Key(urlsafe = urlsafekey)
        card = key.get()

        one = self.request.get("one")
        if one == "":
            one = card.one
        else:
            card.one = one;
            card.put()

        one_one = self.request.get("one_one")
        if one_one == "":
            one_one = card.one_one
        else:
            card.one_one = one_one;
            card.put()

        one_one_one = self.request.get("one_one_one")
		if one_one_one == "":
            one_one_one = card.one_one_one
        else:
            card.one_one_one = one_one_one;
            card.put()

        one_one_two = self.request.get("one_one_two")
		if one_one_two == "":
            one_one_two = card.one_one_two
        else:
            card.one_one_two = one_one_two;
            card.put()

        one_two = self.request.get("one_two")
		if one_two == "":
            one_two = card.one_two
        else:
            card.one_two = one_two;
            card.put()

        one_two_one = self.request.get("one_two_one")
		if one_two_one == "":
            one_two_one = card.one_two_one
        else:
            card.one_two_one = one_two_one;
            card.put()

        one_two_two = self.request.get("one_two_two")
		if one_two_two == "":
            one_two_two = card.one_two_two
        else:
            card.one_two_two = one_two_two;
            card.put()

        two = self.request.get("two")
		if two == "":
			two = card.two
		else:
			card.two = two;
			card.put()

        two_one = self.request.get("two_one")
		if two_one == "":
			two_one = card.two_one
		else:
			card.two_one = two_one;
			card.put()

        two_two = self.request.get("two_two")
		if two_two == "":
			two_two = card.two_two
		else:
			card.two_two = two_two;
			card.put()




        if college == "":
            college = student.college
        else:
            student.college = college;
            student.put()
        if team == "":
            team = student.team
        else:
            student.team = team;
            student.put()


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
