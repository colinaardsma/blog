import gqlqueries
from dbmodels import Users, Blog #import Users and Blog classes from python file named dbmodels

cache = {}
def cached_posts(limit=None, offset=0, user=""):
    key = (limit, offset, user)
    if key in cache:
        r = cache[key]
    else:
        r = gqlqueries.get_posts(limit, offset, user)
        cache[key] = r
    return r

def cached_user_by_name(usr):
    key = (usr)
    if key in cache:
        r = cache[key]
    else:
        r = gqlqueries.get_user_by_name(usr)
        cache[key] = r
    return r

def cached_check_username(username):
    key = (username)
    if key in cache:
        r = cache[key]
    else:
        r = gqlqueries.check_username(username)
        cache[key] = r
    return r
