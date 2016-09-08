import hashlib
import hmac #more secure version of hashlib (when is this best used?)

#start of visit hashing
def make_salt():
    size = 6
    chars = string.ascii_lowercase + string.ascii_uppercase + string.digits #setup list of all uppercase and lowercase letters plus numbers
    #return ''.join(random.choice(chars) for _ in range(size)) #for every blank in string of length 'size' add random choice of uppercase, lowercase, or digits
    return ''.join(random.SystemRandom().choice(chars) for x in range(size)) #more secure version of random.choice, for every blank in string of length 'size' add random choice of uppercase, lowercase, or digits

def make_secure_val(s, salt=""):
    if not salt:
        salt = make_salt() #if salt is empty then get salt value, salt will be empty if making a new value and will not be empty if validating an existing value
    h = hashlib.sha256(s + salt).hexdigest()
    return "%s|%s|%s" % (s, h, salt) #return s|hash value|salt value

def check_secure_val(h):
    s = h.split("|")[0] #pull un-hashed value (s) from s|hash value|salt value
    salt = h.split("|")[2] #pull salt value from s|hash value|salt value
    if h == make_secure_val(s, salt): #check if hash value is valid for h
        return s
#end of visit hashing
