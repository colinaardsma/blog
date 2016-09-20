import os
import webapp2
import jinja2
import math
import hashlib
import hmac #more secure version of hashlib (when is this best used?)
import string
import random
import re #regular expersions
import hashing #import python file named hashing

from google.appengine.ext import db

#setup jinja2
template_dir = os.path.join(os.path.dirname(__file__), 'templates') #set template_dir to main.py dir(current dir)/templates
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True) #set jinja2's working directory to template_dir

#start of GQL queries
def get_posts_pagination(limit, offset):
    return db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC LIMIT %d OFFSET %d" % (limit, offset)) #pulls limit number of posts start at post offset, this allows for pagination

def get_user_posts_pagination(usr, limit, offset):
    # query = Blog.all().filter("author", usr).order("-created")
    # return query.fetch(limit=limit, offset=offset)
    return db.GqlQuery("SELECT * FROM Blog WHERE author = 'aghkZXZ-YmxvZ3ISCxIFVXNlcnMYgICAgICAwAkM' ORDER BY created DESC LIMIT %s OFFSET %s" % (limit, offset)) #pulls limit number of posts start at post offset, this allows for pagination

def get_posts():
    return db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC") #table is named Blog because class is named Blog (the class creates the table)

def get_user_by_name(usr):
    """ Get a user object from the db, based on their username """
    user = db.GqlQuery("SELECT * FROM Users WHERE username = '%s'" % usr)
    if user:
        return user
#end of GQL queries

#start of registration information verification
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
    return USER_RE.match(username)

PASS_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
    return PASS_RE.match(password)

EMAIL_RE = re.compile(r"^[\S]+@[\S]+.[\S]+$")
def valid_email(email):
    return EMAIL_RE.match(email)

def check_username(username):
    n = db.GqlQuery("SELECT * FROM Users ORDER BY username") #pull db of userinfo and order by username
    for name in n:
        if name.username == username:
            return name.key().id()
#end of registration information verification

#start of password hasing
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

#end of password hashing

#define some functions that will be used by all pages
class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw): #simplifies self.response.out.write to self.write
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params): #creates the string that will render html using jinja2 with html template named template and parameters named params
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw): #writes the html string created in render_str to the page
        self.write(self.render_str(template, **kw))

    def initialize(self, *a, **kw):
        """
            A filter to restrict access to certain pages when not logged in.
            If the request path is in the global auth_paths list, then the user
            must be signed in to access the path/resource.
        """
        webapp2.RequestHandler.initialize(self, *a, **kw)
        c = self.request.cookies.get('user') #pull cookie value
        uid = ""
        if c:
            u = c.split("|")[0]
            if not valid_user_id(u, c):
                uid = u #set uid to username

        self.user = uid and Users.get_by_id(int(uid))

        if not self.user and self.request.path in auth_paths:
            self.redirect('/login')

#define columns of database objects
class Blog(db.Model):
    title = db.StringProperty(required = True) #sets title to a string and makes it required
    body = db.TextProperty(required = True) #sets title to a text and makes it required (text is same as string but can be more than 500 characters and cannot be indexed)
    created = db.DateTimeProperty(auto_now_add = True) #sets created to equal date/time of creation (this cannot be modified)
    last_modified = db.DateTimeProperty(auto_now = True) #sets last_modified to equal current date/time (this can be modified)
    author = db.ReferenceProperty(required = True) #sets author to username

#define columns of database objects
class Users(db.Model):
    username = db.StringProperty(required = True) #sets username to a string and makes it required
    password = db.StringProperty(required = True) #sets password to a string and makes it required
    email = db.StringProperty(required = False) #sets email to a string and makes it optional
    created = db.DateTimeProperty(auto_now_add = True) #sets created to equal date/time of creation (this cannot be modified)
    last_modified = db.DateTimeProperty(auto_now = True) #sets last_modified to equal current date/time (this can be modified)


class MainPage(Handler):
    def render_list(self, blogs="", page=""):
        c = self.request.cookies.get('user') #pull cookie value
        usr = get_user_from_cookie(c)

        page = self.request.get("page") #pull url query string
        if not page:
            page = 1
        else:
            page = int(page)
        limit = 5 #number of entries displayed per page
        offset = (page - 1) * 5 #calculate where to start offset based on which page the user is on
        blogs = get_posts_pagination(limit, offset)
        lastPage = math.ceil(blogs.count() / limit) #calculate the last page required based on the number of entries and entries displayed per page

        self.render("list.html", blogs=blogs, page=page, lastPage=lastPage, usr=usr)

    def get(self):
        page = self.request.get("page") #set url query string
        self.render_list(page)

class NewPost(Handler):
    def render_post(self, title="", body="", error=""):
        c = self.request.cookies.get('user') #pull cookie value
        usr = get_user_from_cookie(c)
        self.render("post.html", title=title, body=body, error=error, usr=usr)

    def get(self):
        self.render_post()

    def post(self):
        title = self.request.get("title")
        body = self.request.get("body")

        if title and body:
            post = Blog(title = title, body = body, author = self.user) #create new blog object named post
            post.put() #store post in database
            blogID = "/blog/%s" % str(post.key().id())
            self.redirect(blogID) #send you to view post page
        else:
            error = "Please enter both title and body!"
            self.render_post(title, body, error)

class Archive(Handler):
    def render_archive(self, blogs=""):
        c = self.request.cookies.get('user') #pull cookie value
        usr = get_user_from_cookie(c)

        blogs = get_posts() #call get_posts to run GQL query
        self.render("list.html", blogs=blogs, usr=usr)

    def get(self):
        self.render_archive()

class ModifyPost(Handler):
    def render_modify(self, blogs=""):
        c = self.request.cookies.get('user') #pull cookie value
        usr = get_user_from_cookie(c)
        blogs = get_posts() #call get_posts to run GQL query
        self.render("modify_post.html", blogs=blogs, usr=usr)

    def get(self):
        self.render_modify()

class ViewPost(Handler):
    def render_view(self, post_id):
        c = self.request.cookies.get('user') #pull cookie value
        usr = get_user_from_cookie(c)

        post_id = int(post_id) #post_id is stored as a string initially and will need to be tested against an int in view.html
        post = Blog.get_by_id(post_id)
        self.render("view.html", post=post, post_id=post_id, usr=usr)

    def get(self, post_id):
        self.render_view(post_id)

class EditPost(Handler):
    def render_post(self, post_id, title="", body="", error=""):
        c = self.request.cookies.get('user') #pull cookie value
        usr = get_user_from_cookie(c)
        post_id = int(post_id) #post_id is stored as a string initially and will need to be tested against an int in view.html
        post = Blog.get_by_id(post_id) #retrieve row entry from Blog database based on id# in post_id and name it post
        title = post.title #get title of post
        body = post.body #get body of post
        self.render("edit_post.html", post=post, post_id=post_id, title=title, body=body, error=error, usr=usr)

    def get(self, post_id):
        self.render_post(post_id)

    def post(self, post_id, title="", body="", error=""):
        title = self.request.get("title")
        body = self.request.get("body")

        if title and body:
            post_id = int(post_id) #post_id is stored as a string initially and will need to be tested against an int in view.html
            post = Blog.get_by_id(post_id) #retrieve row entry from Blog database based on id# in post_id and name it post
            post.title = title #update post title
            post.body = body #update post body
            post.put() #uopdate post in database (will update modified datetime but not created datetime)
            blogID = "/blog/%s" % str(post_id)
            self.redirect(blogID) #sends you to view post page
        else:
            error = "Please enter both title and body!"
            self.render_post(post_id, title, body, error)

class DeletePost(Handler):
    def render_view(self, post_id):
        post_id = int(post_id) #post_id is stored as a string initially and will need to be tested against an int in view.html
        post = Blog.get_by_id(post_id) #retrieve row entry from Blog database based on id# in post_id and name it post
        post.delete() #remove row entry post from Blog database
        self.redirect("/")

    def get(self, post_id):
        self.render_view(post_id)

class PostsByUser(Handler):
    def render_list(self, usr, user="", page="", blogs=""):
        c = self.request.cookies.get('user') #pull cookie value
        usr = get_user_from_cookie(c)
        user = get_user_by_name(usr)

        page = self.request.get("page") #pull url query string
        if not page:
            page = 1
        else:
            page = int(page)
        limit = 5 #number of entries displayed per page
        offset = (page - 1) * 5 #calculate where to start offset based on which page the user is on
        blogs = get_user_posts_pagination(user, limit, offset)
        lastPage = math.ceil(blogs.count() / limit) #calculate the last page required based on the number of entries and entries displayed per page
        self.render("list.html", blogs=blogs, page=page, lastPage=lastPage, usr=usr)

    def get(self, usr):
        page = self.request.get("page") #set url query string
        self.render_list(usr, page)

class Registration(Handler):
    def render_reg(self, username="", email="", usernameError="", passwordError="", passVerifyError="", emailError=""):
        self.render("registration.html", username=username, email=email, usernameError=usernameError, passwordError=passwordError, passVerifyError=passVerifyError, emailError=emailError)

    def get(self):
        self.render_reg()

    def post(self):
        username = self.request.get("username")
        password = self.request.get("password")
        passVerify = self.request.get("passVerify")
        email = self.request.get("email")
        error = False

        #check password
        if not password: #check if password is blank
            passwordError = "Password cannot be empty"
            error = True
        elif not valid_password(password): #check if password is valid
            passwordError = "Invalid Password"
            error = True
        else:
            passwordError = ""
        #check password verification
        if not passVerify: #check if password verification is blank
            passVerifyError = "Password Verification cannot be empty"
            error = True
        elif password != passVerify: #check if password matches password verification
            passVerifyError = "Passwords do not match"
            error = True
        else:
            passVerifyError = ""
        #check username
        if not username: #check if username is blank
            usernameError = "Username cannot be empty"
            error = True
        elif not valid_username(username): #check if username if valid
            usernameError = "Invalid Username"
            error = True
        elif check_username(username): #check if username is unique
            usernameError = "That username is taken"
            error = True
        else:
            usernameError = ""
        #check email
        if not email: #check if email is blank
            emailError = ""
        elif not valid_email(email): #check if email is valid
            emailError = "Invalid Email"
            error = True
        else:
            emailError = ""
        #see if any errors returned
        if error == False:
            username = username
            password = make_pw_hash(username, password) #hash password for storage in db
            user = Users(username=username, password=password, email=email) #create new blog object named post
            user.put() #store post in database
            user_id = user.key().id()
            self.response.headers.add_header('Set-Cookie', 'user=%s' % make_user_id_hash(user_id)) #hash user id for use in cookie
            self.redirect('/welcome')
        else:
            self.render_reg(username, email, usernameError, passwordError, passVerifyError, emailError)


        # if title and body:
        #     post = Blog(title = title, body = body) #create new blog object named post
        #     post.put() #store post in database
        #     blogID = "/blog/%s" % str(post.key().id())
        #     self.redirect(blogID) #send you to view post page
        # else:
        #     error = "Please enter both title and body!"
        #     self.render_post(title, body, error)

class Login(Handler):
    def render_login(self, username="", error=""):
        self.render("login.html", username=username, error=error)

    def get(self):
        self.render_login()

    def post(self):
        username = self.request.get("username")
        password = self.request.get("password")

        if not check_username(username):
            error = "Invalid login"
        else:
            user_id = check_username(username)
            user_id = int(user_id)
            u = Users.get_by_id(user_id)
            p = u.password
            salt = p.split("|")[1]
            if username == u.username:
                if make_pw_hash(username, password, salt) == p:
                    error = ""
                else:
                    error = "invalid login - pass"

        if error:
            self.render_login(username, error)
        else:
            self.response.headers.add_header('Set-Cookie', 'user=%s' % make_user_id_hash(user_id)) #hash user id for use in cookie
            self.redirect('/welcome')

class Logout(Handler):
    def get(self):
        self.response.headers.add_header('Set-Cookie', 'user=""; expires=Thu, 01-Jan-1970 00:00:10 GMT') #clear cookie
        self.redirect('/registration')

class Welcome(Handler):
    def render_welcome(self):
        c = self.request.cookies.get('user') #pull cookie value
        usr = get_user_from_cookie(c)

        self.redirect('/')

    def get(self):
        self.render_welcome()

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/new_post', NewPost),
    ('/archive', Archive),
    ('/modify_post', ModifyPost),
    webapp2.Route('/blog/<post_id:\d+>', ViewPost),
    webapp2.Route('/blog/<post_id:\d+>/edit', EditPost),
    webapp2.Route('/blog/<post_id:\d+>/delete', DeletePost),
    webapp2.Route('/blog/<usr:[a-zA-Z0-9_-]{3,20}>', PostsByUser),
    ('/registration', Registration),
    ('/login', Login),
    ('/logout', Logout),
    ('/welcome', Welcome)
], debug=True)

auth_paths = [ #must be logged in to access these links
    '/new_post',
    '/modify_post',
    '/blog/<post_id:\d+>/edit',
    '/blog/<post_id:\d+>/delete'
]
