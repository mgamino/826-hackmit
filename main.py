import webapp2
import jinja2
import os
from google.appengine.api import users
from google.appengine.ext import ndb
import logging
import smtplib

#TODO: AGE OH Y GOD

#These are the ndb Models
class Profile (ndb.Model):
    name = ndb.StringProperty()
    bio = ndb.TextProperty()
    accountCreated = ndb.DateTimeProperty(auto_now_add=True)
    email = ndb.StringProperty()
    age = ndb.IntegerProperty()

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
    approval = ndb.BooleanProperty()

class Card(ndb.Model):
    text = ndb.TextProperty()
    story_key = ndb.KeyProperty(kind = Story)
    cardNumber = ndb.StringProperty()

# class Submission(ndb.Model):
# 	text = ndb.TextProperty()
# 	profile_email = ndb.StringProperty()
#
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))

#These are the handlers for the HTML templates

#main complete!
class MainHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()

        if user:
            email = user.email().lower()
            logout_url=users.CreateLogoutURL('/')

            profile = Profile.query(Profile.email == email).fetch()
            if (len(profile) <1):
                profile = Profile(name = "Amazing Author", bio = "I love storytelling!", email = email)
                profile.put()
                self.redirect("/main.html")

            template_vals = {'profile':profile, 'logout_url':logout_url}
            template = jinja_environment.get_template("main.html")
            self.response.write(template.render(template_vals))
        else:
            login_url = users.CreateLoginURL('/')
            template = jinja_environment.get_template("login.html")
            template_vals = {'login_url':login_url}
            self.response.write(template.render(template_vals))

#profile complete!
class ProfileHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        profile = Profile.query(Profile.email == user.email()).fetch()

        logout_url=users.CreateLogoutURL('/')

        # publishedStories = Story.query(Story.profile_key == profile.key, Story.published == True)
        # inProgressStories = Story.query(Story.profile_key == profile.key, Story.published==False, Story.submitted == True).fetch()
        # draftStories = Story.query(Story.profile_key==profile.key, Story.submitted==False).fetch()

        template = jinja_environment.get_template("profile.html")
        template_vals = {'profile':profile, 'logout_url':logout_url} #'publishedStories':publishedStories, 'inProgressStories':inProgressStories, 'draftStories':draftStories}

        self.response.write(template.render(template_vals))

#set profile complete!
class SetProfileHandler(webapp2.RequestHandler):
    def get(self):
        urlsafe_key = self.request.get('key')
        key = ndb.Key(urlsafe = urlsafe_key)
        profile = key.get()

        logout_url=users.CreateLogoutURL('/')

        template = jinja_environment.get_template("make-profile.html")
        template_vals = {'profile':profile, 'logout_url':logout_url}

        self.response.write(template.render(template_vals))

    def post(self):
        urlsafe_key = self.request.get('key')
        key = ndb.Key(urlsafe = urlsafe_key)
        profile = key.get()

        name = self.request.get('name')
        if name == "":
            name = profile.name
        else:
            profile.name = name
        bio = self.request.get('bio')
        if bio == "":
            bio = profile.bio
        else:
            profile.bio = bio

        age = self.request.get('age')
        if age == "":
            age = profile.age
        else:
            profile.age = age

        profile.put()
        self.redirect('/profile')

#read page comlpete!
class ReadHandler(webapp2.RequestHandler):
    def get(self):
        stories = Story.query(Story.published == True).fetch()

        template = jinja_environment.get_template("read.html")
        template_vals = {'stories':stories}
        self.response.write(template.render(template_vals))

#possigly combine these two things! who gives a fuck! otherwise done!
class ReadCyoaHandler(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template("readcyoa.html")
        urlsafe_key = self.request.get('key')
        key = ndb.Key(urlsafe = urlsafe_key)
        story = key.get()

        template_vals = {'story':story}

        self.response.write(template.render(template_vals))

#see above!
class ReadFreewriteHandler(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template("readcyoa.html")
        urlsafe_key = self.request.get('key')
        key = ndb.Key(urlsafe = urlsafe_key)
        story = key.get()

        template_vals = {'story':story}

        self.response.write(template.render(template_vals))

#TODO: once you have the HTML, merge freewrite and cyoa into this, using if-else statements based on the form name
class WriteHandler(webapp2.RequestHandler):
    def get(self):

        user = users.get_current_user()
        email = user.email()
        profile = Profile.query(Profile.email == email).fetch()

        template = jinja_environment.get_template("write.html")
        template_vals = {'profile':profile}
        self.response.write(template.render(template_vals))

    def post(self):
        urlsafe_key = self.request.get('key')
        key = ndb.Key(urlsafe = urlsafe_key)
        story = key.get()

        user = users.get_current_user()
        email = user.email()
        profile = Profile.query(Profile.email == email).fetch()

        title = self.request.get('title')
        theme = self.request.get('theme')
        structure = self.request.get('structure')

        story = Story(title = title, profile_key = profile, theme = theme, structure = structure, views = 0, published = False, approval = False)
        story.put()
        self.redirect('/profile')

# class FreewriteHandler(webapp2.RequestHandler):
#     def get(self):
#         #TODO: something about loading the story key?? from url maybe??
#         template = jinja_environment.get_template("freewrite.html")
#         self.response.write(template.render())
#     #TODO: def post(self): save the card & story
#
# 	def post(self):
# 		text = self.request.get('text')
#         urlsafe_key = self.request.get('key')
#         key = ndb.Key(urlsafe = urlsafe_key)
#         story = key.get()
#
# 		card = Card(text = text, story_key = story_key, cardNumber = "1")
# 		card.put()
# 		self.redirect("/profile")

# class CyoaHandler(webapp2.RequestHandler):
#     def get(self):
#         urlsafe_key = self.request.get('key')
#         key = ndb.Key(urlsafe = urlsafe_key)
#
#         story = key.get()
#
#         template_vals = {'story':story}
#         template = jinja_environment.get_template("cyoa.html")
#         self.response.write(template.render())
#     def post(self):
#         urlsafekey = self.request.get('key')
#         key = ndb.Key(urlsafe = urlsafekey)
#         card = key.get()
#
#         one = self.request.get("one")
#         if one == "":
#             one = card.one
#         else:
#             card.one = one;
#             card.put()
#
#         one_one = self.request.get("one_one")
#         if one_one == "":
#             one_one = card.one_one
#         else:
#             card.one_one = one_one;
#             card.put()
#
#         one_one_one = self.request.get("one_one_one")
# 		if one_one_one == "":
#             one_one_one = card.one_one_one
#         else:
#             card.one_one_one = one_one_one;
#             card.put()
#
#         one_one_two = self.request.get("one_one_two")
# 		if one_one_two == "":
#             one_one_two = card.one_one_two
#         else:
#             card.one_one_two = one_one_two;
#             card.put()
#
#         one_two = self.request.get("one_two")
# 		if one_two == "":
#             one_two = card.one_two
#         else:
#             card.one_two = one_two;
#             card.put()
#
#         one_two_one = self.request.get("one_two_one")
# 		if one_two_one == "":
#             one_two_one = card.one_two_one
#         else:
#             card.one_two_one = one_two_one;
#             card.put()
#
#         one_two_two = self.request.get("one_two_two")
# 		if one_two_two == "":
#             one_two_two = card.one_two_two
#         else:
#             card.one_two_two = one_two_two;
#             card.put()
#
#         two = self.request.get("two")
# 		if two == "":
# 			two = card.two
# 		else:
# 			card.two = two;
# 			card.put()
#
#         two_one = self.request.get("two_one")
# 		if two_one == "":
# 			two_one = card.two_one
# 		else:
# 			card.two_one = two_one;
# 			card.put()
#
#         two_two = self.request.get("two_two")
# 		if two_two == "":
# 			two_two = card.two_two
# 		else:
# 			card.two_two = two_two;
# 			card.put()

# class SubmitHandler(webapp2.RequestHandler):
#     def get(self):
#         template = jinja_environment.get_template("submit.html")
#         self.response.write(template.render())
#
# 	def post(self):
# 		text = self.request.get('text')
# 		profile = users.get_current_user()
# 		profile_email = profile.email().lower()
#
# 		submission = Submission(text = text, profile_email = profile_email)
# 		submission.put()
# 		self.redirect("/submitted")

#submitted for approval confirmation done!
class SubmittedHandler(webapp2.RequestHandler):
	def get(self):
		template = jinja_environment.get_template("submitted.html")
		self.response.write(template.render())

#TODO: please get the profile info from the story key also pls
class ApprovalFormHandler(webapp2.RequestHandler):
    def get(self):

        urlsafe_key = self.request.get('key')
        key = ndb.Key(urlsafe = urlsafe_key)

        story = key.get()


        template = jinja_environment.get_template("approvalform.html")
        template_vals = {'story':story}

        self.response.write(template.render(template_vals))
    def post(self):
        urlsafe_key = self.request.get('key')
        key = ndb.Key(urlsafe = urlsafe_key)
        story = key.get()
        approval = request.get('approval')

        if approval == 'Yes':
            story.approval = True
        story.put()

        self.redirect('/approvalconfirm')

#approval confirmation page!
class ApprovalConfirmHandler(webapp2.RequestHandler):
    def get(self):
        urlsafe_key = self.request.get('key')
        key = ndb.Key(urlsafe = urlsafe_key)
        story = key.get()

        template = jinja_environment.get_template("approvalconfirm.html")
        template_vals = {'story':story}
        self.response.write(template.render(template_vals))

#ya pls update all of this
app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/main.html', MainHandler),
    ('/index.html',MainHandler),
    ('/profile.html', ProfileHandler),
    ('/make-profile', SetProfileHandler),
    ('/read.html', ReadHandler),
#    ('/readcyoa',ReadCyoaHandler),
#    ('/readfreewrite',ReadFreewriteHandler),
    ('/write.html',WriteHandler),
#    ('/submit', SubmitHandler),
	('/submitted',SubmittedHandler),
    ('/approvalform', ApprovalFormHandler),
    ('/approvalconfirm', ApprovalConfirmHandler),
], debug=True)
