from google.appengine.ext import db

#define columns of database objects
class Users(db.Model):
    username = db.StringProperty(required = True) #sets username to a string and makes it required
    password = db.StringProperty(required = True) #sets password to a string and makes it required
    email = db.StringProperty(required = False) #sets email to a string and makes it optional
    created = db.DateTimeProperty(auto_now_add = True) #sets created to equal date/time of creation (this cannot be modified)
    last_modified = db.DateTimeProperty(auto_now = True) #sets last_modified to equal current date/time (this can be modified)

#define columns of database objects
class Blog(db.Model):
    title = db.StringProperty(required = True) #sets title to a string and makes it required
    body = db.TextProperty(required = True) #sets title to a text and makes it required (text is same as string but can be more than 500 characters and cannot be indexed)
    created = db.DateTimeProperty(auto_now_add = True) #sets created to equal date/time of creation (this cannot be modified)
    last_modified = db.DateTimeProperty(auto_now = True) #sets last_modified to equal current date/time (this can be modified)
    author = db.ReferenceProperty(Users, required = True) #sets author to username
    coords = db.GeoPtProperty(required = False) #store coordinates of user based on URL, not required as it may not always be available
