import gqlqueries
from dbmodels import Users, Blog #import Users and Blog classes from python file named dbmodels
from google.appengine.api import memcache

def cached_posts(limit=None, offset=0, user="", update=False):
    key = str(limit) + str(offset) + str(user)
    blogs = memcache.get(key)
    if blogs is None or update:
        blogs = gqlqueries.get_posts(limit, offset, user)
        memcache.set(key, blogs)
    return blogs

def cached_user_by_name(usr, update=False):
    key = str(usr) + "getUser"
    user = memcache.get(key)
    if user is None or update:
        user = gqlqueries.get_user_by_name(usr)
        memcache.set(key, user)
    return user

def cached_check_username(username, update=False):
    key = str(username) + "checkUsername"
    name = memcache.get(key)
    if name is None or update:
        name = gqlqueries.check_username(username)
        memcache.set(key, name)
    return name
