import gqlqueries
from dbmodels import Users, Blog #import Users and Blog classes from python file named dbmodels

POST_CACHE = {}
def cached_posts(limit=None, offset=0, user="", update=False):
    key = (limit, offset, user)
    if not update and key in POST_CACHE:
        r = POST_CACHE[key]
    else:
        r = gqlqueries.get_posts(limit, offset, user)
        POST_CACHE[key] = r
    return r

USER_BY_NAME_CACHE = {}
def cached_user_by_name(usr, update=False):
    key = (usr)
    if key in USER_BY_NAME_CACHE:
        r = USER_BY_NAME_CACHE[key]
    else:
        r = gqlqueries.get_user_by_name(usr)
        USER_BY_NAME_CACHE[key] = r
    return r

USERNAME_CACHE = {}
def cached_check_username(username, update=False):
    key = (username)
    if key in USERNAME_CACHE:
        r = USERNAME_CACHE[key]
    else:
        r = gqlqueries.check_username(username)
        USERNAME_CACHE[key] = r
    return r
