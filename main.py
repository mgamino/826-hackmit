import webapp2
import jinja2
import os
from google.appengine.api import users
from google.appengine.ext import ndb
import logging
import smtplib

# TODO(asap!):
    # - profile & editprofile: add {{profile.email}} somewhere in html
    # - profile & editprofile: add avatar to HTML (dropdown OR radio button in makeprofile)
    # - ALL html: check to make sure logout_url is linked correctly
    # - fix webflow please im screaming
    # - editstory page - linked from story URL if it is your story & not published
    # - editstory page - prepopulated form? research!
    # - do the python comma thing
    # - the email thing smtplib? maybe?
    # - approvalform html - need form


# TODO(whenever!):
    #  - cyoa story cards
    #  - cyoa html wowie
    #  - please add some kind of about page lmao - publicProfile.html for m, l2, l5, 826 in general?

def getProfile():
    user = users.get_current_user()
    profiles = Profile.query(Profile.email == user.email().lower()).fetch()
    profile = profiles[0]
    return profile

#These are the ndb Models
class Profile (ndb.Model):
    name = ndb.StringProperty()
    bio = ndb.TextProperty()
    avatar = ndb.StringProperty()
    accountCreated = ndb.DateTimeProperty(auto_now_add=True)
    email = ndb.StringProperty()
    age = ndb.StringProperty()

class Story (ndb.Model):
    title = ndb.StringProperty()
    author_key = ndb.KeyProperty(kind = Profile)
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

# class PromptSubmission(ndb.Model):
# 	text = ndb.TextProperty()
# 	author_key = ndb.KeyProperty(kind = Profile)

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))

#main complete!
class MainHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()

        if user:
            email = user.email().lower()
            profiles = Profile.query(Profile.email == email).fetch()
            logout_url=users.create_logout_url('/')

            if (len(profiles)>0):
                logging.info("hahhahaaha what the fuck")
                profile = profiles[0]
                template_vals = {'profile':profile, 'logout_url':logout_url}
                template = jinja_environment.get_template("main.html")
                self.response.write(template.render(template_vals))
            else:
                template = jinja_environment.get_template("newprofile.html")
                template_vals = {'logout_url':logout_url}
                self.response.write(template.render(template_vals))

        else:
            login_url = users.create_login_url('/')
            template = jinja_environment.get_template("login.html")
            template_vals = {'login_url':login_url}
            self.response.write(template.render(template_vals))

    def post(self):
        user = users.get_current_user()
        email = user.email().lower()

        name = self.request.get('name')
        bio = self.request.get('bio')
        age = self.request.get('age')
        avatar = 'ok'

        profile = Profile(email = email, name = name, bio = bio, age = age, avatar = avatar)
        profile.put()
        logging.info("PROFILE HELP")
        logging.info(profile)
        self.redirect('/createdprofile')

#profile complete!
class ProfileHandler(webapp2.RequestHandler):
    def get(self):
        profile = getProfile()

        logout_url=users.create_logout_url('/')
        draftStories = Story.query(Story.author_key==profile.key, Story.published==False).fetch()
        waitingStories = Story.query(Story.author_key == profile.key, Story.published==True, Story.approval == False).fetch()
        publishedStories = Story.query(Story.author_key == profile.key, Story.approval == True).fetch()

        template_vals = {'profile':profile, 'logout_url':logout_url, 'draftStories':draftStories, 'publishedStories':publishedStories, 'waitingStories': waitingStories,}
        template = jinja_environment.get_template("profile.html")
        self.response.write(template.render(template_vals))

#set profile complete!
class EditProfileHandler(webapp2.RequestHandler):
    def get(self):
        profile = getProfile()

        logout_url=users.create_logout_url('/')

        template_vals = {'profile':profile, 'logout_url':logout_url}
        template = jinja_environment.get_template("editprofile.html")
        self.response.write(template.render(template_vals))

    def post(self):
        profile = getProfile()

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

        avatar = self.request.get('avatar')
        profile.avatar = avatar

        profile.put()
        self.redirect('/')

class CreatedProfileHandler(webapp2.RequestHandler):
    def get(self):

        logout_url=users.create_logout_url('/')

        template_vals = {'logout_url':logout_url}
        template = jinja_environment.get_template("createdprofile.html")
        self.response.write(template.render(template_vals))


#read page comlpete!
class ReadHandler(webapp2.RequestHandler):
    def get(self):
        stories = Story.query(Story.approval == True).fetch()

        template = jinja_environment.get_template("read.html")
        template_vals = {'stories':stories}
        self.response.write(template.render(template_vals))

# class ReadCyoaHandler(webapp2.RequestHandler):
#     def get(self):
#         template = jinja_environment.get_template("readcyoa.html")
#         urlsafe_key = self.request.get('key')
#         key = ndb.Key(urlsafe = urlsafe_key)
#         story = key.get()
#
#         template_vals = {'story':story}
#
#         self.response.write(template.render(template_vals))

class FreeStyleStoryHandler(webapp2.RequestHandler):
    def get(self):
        profile = getProfile()

        story_key_urlsafe = self.request.get('key')
        key = ndb.Key(urlsafe = story_key_urlsafe)
        story = key.get()

        cards = Card.query(Card.story_key == story.key).fetch()
        card = cards[0]

        authors = Profile.query(Profile.key == story.author_key).fetch()
        author = authors[0]

        logout_url=users.create_logout_url('/')

        template = jinja_environment.get_template("freestylestory.html")
        template_vals = {'story':story, 'profile':profile, 'author':author, 'card':card, 'logout_url':logout_url}
        self.response.write(template.render(template_vals))

class WriteHandler(webapp2.RequestHandler):
    def get(self):
        profile = getProfile()

        logout_url=users.create_logout_url('/')

        template = jinja_environment.get_template("write.html")
        template_vals = {'profile':profile, 'logout_url':logout_url}
        self.response.write(template.render(template_vals))

    def post(self):
        profile = getProfile()

        title = self.request.get('title')
        theme = self.request.get('theme')
        text = self.request.get('text')
        structure = "freewrite"

        story = Story(title = title, author_key = profile.key, theme = theme, structure = structure, views = 0, published = False, approval = False)
        story.put()

        card = Card(text = text, story_key = story.key)
        card.put()
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

#TODO: please get the profile info from the story key also pls

class ApprovalFormHandler(webapp2.RequestHandler):
    def get(self):
        urlsafe_key = self.request.get('key')
        key = ndb.Key(urlsafe = urlsafe_key)
        story = key.get()

        card = Card.query(Card.story_key == story.key).fetch()

        authors = Profile.query(Profile.key == story.author_key).fetch()
        author = authors[0]

        template = jinja_environment.get_template("freestyleapprovalform.html")
        template_vals = {'story':story, 'author':author, 'card':card}

        self.response.write(template.render(template_vals))

    def post(self):
        urlsafe_key = self.request.get('key')
        key = ndb.Key(urlsafe = urlsafe_key)
        story = key.get()

        approval = self.request.get('approval')

        if approval == 'Yes':
            story.approval = True
        else:
            story.published = False
        story.put()

        self.redirect('/approvalconfirm')

#approval confirmation page!
class ApprovalConfirmHandler(webapp2.RequestHandler):
    def get(self):
        urlsafe_key = self.request.get('key')
        key = ndb.Key(urlsafe = urlsafe_key)
        story = key.get()

        authors = Profile.query(Profile.key == story.author_key).fetch()
        author = authors[0]

        template = jinja_environment.get_template("freestyleapprovalconfirm.html")
        template_vals = {'story':story, 'author':author}
        self.response.write(template.render(template_vals))

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/main.html', MainHandler),
    ('/index.html',MainHandler),
    ('/main', MainHandler),
    ('/index', MainHandler),

    ('/profile.html', ProfileHandler),
    ('/profile', ProfileHandler),

    ('/editprofile.html', EditProfileHandler),
    ('/editprofile', EditProfileHandler),

    ('/createdprofile.html', CreatedProfileHandler),
    ('/createdprofile', CreatedProfileHandler),

    ('/read.html', ReadHandler),
    ('/read', ReadHandler),

    ('/write.html',WriteHandler),
    ('/write', WriteHandler),

    ('/freestylestory.html', FreeStyleStoryHandler),
    ('/freestylestory', FreeStyleStoryHandler),

    ('/approvalform.html', ApprovalFormHandler),
    ('/approvalconfirm.html', ApprovalConfirmHandler),
    ('/approvalform', ApprovalFormHandler),
    ('/approvalconfirm', ApprovalConfirmHandler),
], debug=True)
