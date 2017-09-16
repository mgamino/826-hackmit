# 826-hackmit
PAGES '/' home.html MainHandler home page,  '/profile' profile.html ProfileHandler shows user profile info, '/setprofile' setprofile.html SetProfileHandler used for editing profile, '/read' read.html ReadHandler used for reading stories, '/readcyoa' readcyoa.html ReadCyoaHandler used for reading cyoa stories, '/readfreewrite' readfreewrite.html ReadFreewriteHandler used for reading freewrite stories, '/write' write.html used for the setup of story writing, '/freewrite' freewrite.html FreeWriteHandler used for writing freewrite stories, '/cyoa' cyoa.html CyoaHandler used for writing cyoa stories, '/submit' submit.html SubmitHandler used for submitting prompt ideas, '/submitted' submitted.html SubmittedHandler shown upon successful submission of prompt idea

PROFILE class name StringProperty user full name, bio TextProperty user bio, accountCreated DateTimeProperty date of account creation

STORY class title StringProperty title of story, profile_email StringProperty email of author, publicationDate DateTimeProperty date of publication, writtenDate DateTimeProperty date story was written, prompt TextProperty prompt of story, visualTheme StringProperty theme associated with prompt, structure StringProperty structure used for story creation, views IntegerProperty number of views on story, published BooleanProperty true if story has been published

STORYCARD class text TextProperty content of storycard, story_key KeyProperty story for which card is written, cardNumber StringProperty number of storycard

SUBMISSION class text TextProperty content of prompt submission, profile_email StringProperty email of user submitting prompt
