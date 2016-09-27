import hashlib, hmac #hmac is more secure version of hashlib (when is this best used?)
from dbmodels import Users #import Users class from python file named dbmodels
import string
import random

""" fucntions for hasing and checking password values """
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

""" functions for hashing and checking cookie values """
secret = "DF*BVG#$4oinm5bEBN46o0j594pmve345@63"
def hash_str(s):
    return hmac.new(secret,s).hexdigest()

def make_secure_val(s):
    s = str(s)
    return "%s|%s" % (s, hash_str(s))

def check_secure_val(h):
    s = h.split("|")[0]
    if h == make_secure_val(s):
        return s

""" functions to retrieve username """
def get_username(h):
    user_id = check_secure_val(h)
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
