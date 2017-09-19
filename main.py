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
    age = ndb.StringProperty()

class Story (ndb.Model):
    title = ndb.StringProperty()
    profile_key = ndb.KeyProperty(kind = Profile)
    publicationDate = ndb.DateTimeProperty()
    writtenDate = ndb.DateTimeProperty(auto_now_add=True)
    theme = ndb.StringProperty()
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
            logout_url=users.create_logout_url('/')
            profiles = Profile.query(Profile.email == email).fetch()

            profile = profiles[0]

            if (len(profiles) <1):
                profile = Profile(name = "Amazing Author", bio = "I love storytelling!", email = email, age = "ageless")
                profile.put()
                self.redirect("/main.html")

            template_vals = {'profile':profile, 'logout_url':logout_url}
            template = jinja_environment.get_template("main.html")
            self.response.write(template.render(template_vals))
        else:
            login_url = users.create_login_url('/')
            template = jinja_environment.get_template("login.html")
            template_vals = {'login_url':login_url}
            self.response.write(template.render(template_vals))

#profile complete!
class ProfileHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()

        profiles = Profile.query(Profile.email == user.email().lower()).fetch()
        profile = profiles[0]

        logging.info("profpls")
        logging.info(profile)

        logout_url=users.create_logout_url('/')

        # publishedStories = Story.query(Story.profile_key == profile.key, Story.published == True)
        # inProgressStories = Story.query(Story.profile_key == profile.key, Story.published==False, Story.submitted == True).fetch()
        draftStories = Story.query(Story.profile_key==profile.key, Story.published==False).fetch()

        template = jinja_environment.get_template("profile.html")
        template_vals = {'profile':profile, 'logout_url':logout_url, 'draftStories':draftStories} #'publishedStories':publishedStories, 'inProgressStories':inProgressStories, 'draftStories':draftStories}

        self.response.write(template.render(template_vals))

#set profile complete!
class MakeProfileHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        profile = Profile.query(Profile.email == user.email()).fetch()

        logout_url=users.create_logout_url('/')

        template = jinja_environment.get_template("makeprofile.html")
        template_vals = {'profile':profile, 'logout_url':logout_url}

        self.response.write(template.render(template_vals))

    def post(self):
        user = users.get_current_user()
        profiles = Profile.query(Profile.email == user.email()).fetch()
        profile = profiles[0]

        name = self.request.get('name')
        if name == "":
            name = profile.name
        else:
            profile.name = name
            profile.put()

        bio = self.request.get('bio')
        if bio == "":
            bio = profile.bio
        else:
            profile.bio = bio
            profile.put()

        age = self.request.get('age')
        if age == "":
            age = profile.age
        else:
            profile.age = age
            profile.put()

        profile.put()
        self.redirect('/profile.html')

#read page comlpete!
class ReadHandler(webapp2.RequestHandler):
    def get(self):
        stories = Story.query(Story.approval == True).fetch()

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
class FreeStyleStoryHandler(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template("freestylestory.html")
        story_key_urlsafe = self.request.get('key')
        key = ndb.Key(urlsafe = story_key_urlsafe)
        story = key.get()

        cards = Card.query(Card.story_key == story.key).fetch()
        card = cards[0]

        logging.info("CARD IS")
        logging.info(card.text)

        user = users.get_current_user()
        profiles = Profile.query(Profile.email == user.email()).fetch()
        profile = profiles[0]

        authors = Profile.query(Profile.key == story.profile_key).fetch()
        logging.info(authors)
        author = authors[0]

        logging.info("AUTHOR IS: ")
        logging.info(author)

        template_vals = {'story':story, 'profile':profile, 'author':author, 'card':card}

        self.response.write(template.render(template_vals))

#TODO: once you have the HTML, merge freewrite and cyoa into this, using if-else statements based on the form name
class WriteHandler(webapp2.RequestHandler):
    def get(self):

        user = users.get_current_user()
        email = user.email()
        profiles = Profile.query(Profile.email == email).fetch()
        profile = profiles[0]

        template = jinja_environment.get_template("write.html")
        template_vals = {'profile':profile}
        self.response.write(template.render(template_vals))

    def post(self):
        user = users.get_current_user()
        email = user.email()
        profiles = Profile.query(Profile.email == email).fetch()
        profile = profiles[0]

        title = self.request.get('title')
        theme = self.request.get('theme')
        text = self.request.get('text')
        structure = "freewrite"

        story = Story(title = title, profile_key = profile.key, theme = theme, structure = structure, views = 0, published = False, approval = True)
        story.put()

        card = Card(text = text, story_key = story.key)
        card.put()

        logging.info("POST COMPLETE")
        self.redirect('/profile.html')

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
    ('/makeprofile.html', MakeProfileHandler),
    ('/read.html', ReadHandler),
    ('/read', ReadHandler),
#    ('/readcyoa',ReadCyoaHandler),
    ('/freestylestory',FreeStyleStoryHandler),
    ('/write.html',WriteHandler),
#    ('/submit', SubmitHandler),
	('/submitted',SubmittedHandler),
    ('/approvalform', ApprovalFormHandler),
    ('/approvalconfirm', ApprovalConfirmHandler),
], debug=True)
