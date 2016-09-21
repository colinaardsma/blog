from dbmodels import Users, Blog #import Users and Blog classes from python file named dbmodels
from google.appengine.ext import db

def get_posts(limit=None, offset=0, user=""):
    if user:
        query = Blog.all().filter("author", user).order("-created") # .all() = "SELECT *"; .filter("author", user) = "author = user"; .order("-created") = "ORDER BY created DESC"
    else:
        query = Blog.all().order("-created") # .all() = "SELECT *"; .order("-created") = "ORDER BY created DESC"
    return query.fetch(limit=limit, offset=offset) # .fetch(limit=limt, offset=offset) = "LIMIT limit OFFSET offset"
    # return db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC") #table is named Blog because class is named Blog (the class creates the table)

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
