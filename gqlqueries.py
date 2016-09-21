from dbmodels import Users, Blog #import Users and Blog classes from python file named dbmodels
from google.appengine.ext import db

def get_posts_pagination(limit, offset):
    return db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC LIMIT %d OFFSET %d" % (limit, offset)) #pulls limit number of posts start at post offset, this allows for pagination

def get_user_posts_pagination(usr, limit, offset):
    # query = Blog.all().filter("author", usr).order("-created")
    # return query.fetch(limit=limit, offset=offset)
    return db.GqlQuery("SELECT * FROM Blog WHERE author = '%s' ORDER BY created DESC LIMIT %s OFFSET %s" % (usr, limit, offset)) #pulls limit number of posts start at post offset, this allows for pagination

def get_posts():
    return db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC") #table is named Blog because class is named Blog (the class creates the table)

def get_user_by_name(usr):
    """ Get a user object from the db, based on their username """
    user = db.GqlQuery("SELECT * FROM Users WHERE username = '%s'" % usr)
    if user:
        return user.get()

def check_username(username):
    n = db.GqlQuery("SELECT * FROM Users ORDER BY username") #pull db of userinfo and order by username
    for name in n:
        if name.username == username:
            return name.key().id()
