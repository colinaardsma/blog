import hashlib
import hmac #more secure version of hashlib (when is this best used?)
from dbmodels import Users #import Users class from python file named dbmodels
import string
import random

def make_salt():
    size = 6
    chars = string.ascii_lowercase + string.ascii_uppercase + string.digits #setup list of all uppercase and lowercase letters plus numbers
    #return ''.join(random.choice(chars) for _ in range(size)) #for every blank in string of length 'size' add random choice of uppercase, lowercase, or digits
    return ''.join(random.SystemRandom().choice(chars) for x in range(size)) #more secure version of random.choice, for every blank in string of length 'size' add random choice of uppercase, lowercase, or digits

def make_pw_hash(name, pw, salt=""): #for storage in db
    if not salt:
        salt = make_salt() #if salt is empty then get salt value, salt will be empty if making a new value and will not be empty if validating an existing value
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return "%s|%s" % (h, salt)

def valid_pw(name, pw, h):
    salt = h.split("|")[1] #split h by "|" and set salt to data after pipe (h is hash,salt)
    if h == make_hash(name, pw, salt):
        return True

def make_user_id_hash(user_id, salt=""): #for use in cookie
    user_id = int(user_id)
    if not Users.get_by_id(user_id):
        return
    else:
        user = Users.get_by_id(user_id) #currently crashes here if id is invalid
        name = user.username
        pw = user.password
        if not salt:
            salt = make_salt() #if salt is empty then get salt value, salt will be empty if making a new value and will not be empty if validating an existing value
            h = hashlib.sha256(name + pw + salt).hexdigest()
            return "%s|%s|%s" % (user_id, h, salt)

def valid_user_id(user_id, h):
    salt = h.split("|")[2]
    if h == make_user_id_hash(user_id, salt):
        return True

def get_username(h):
    user_id = h.split("|")[0]
    user_id = int(user_id)
    if not Users.get_by_id(user_id):
        return
    else:
        user = Users.get_by_id(user_id) #currently crashes here if id is invalid
        username = user.username
        return username

def get_user_from_cookie(c):
        if c:
            usr = get_username(c) #set usr to username
        else:
            usr = "" #if no cookie set usr to blank
        return usr
