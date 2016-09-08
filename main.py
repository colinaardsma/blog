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
    return db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC LIMIT %s OFFSET %s" % (limit, offset)) #pulls limit number of posts start at post offset, this allows for pagination

def get_posts():
    return db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC") #table is named Blog because class is named Blog (the class creates the table)
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

#define columns of database objects
class Blog(db.Model):
    title = db.StringProperty(required = True) #sets title to a string and makes it required
    body = db.TextProperty(required = True) #sets title to a text and makes it required (text is same as string but can be more than 500 characters and cannot be indexed)
    created = db.DateTimeProperty(auto_now_add = True) #sets created to equal date/time of creation (this cannot be modified)
    last_modified = db.DateTimeProperty(auto_now = True) #sets last_modified to equal current date/time (this can be modified)

#define columns of database objects
class Users(db.Model):
    username = db.StringProperty(required = True) #sets username to a string and makes it required
    password = db.StringProperty(required = True) #sets password to a string and makes it required
    email = db.StringProperty(required = False) #sets email to a string and makes it optional
    created = db.DateTimeProperty(auto_now_add = True) #sets created to equal date/time of creation (this cannot be modified)
    last_modified = db.DateTimeProperty(auto_now = True) #sets last_modified to equal current date/time (this can be modified)


class MainPage(Handler):
    def render_list(self, blogs="", page=""):
        c = self.request.cookies.get('user')
        username = ""
        if c:
            user_id = c.split("|")[0]
            # user_id = int(user_id)
            if valid_user_id(user_id, c):
                user = Users.get_by_id(user_id)
                username = user.username
            else:
                # self.response.headers.add_header('Set-Cookie', 'user=""; expires=0') #hash user id for use in cookie
                self.redirect('/registration')

        page = self.request.get("page") #pull url query string
        if not page:
            page = 1
        else:
            page = int(page)
        limit = 5 #number of entries displayed per page
        offset = (page - 1) * 5 #calculate where to start offset based on which page the user is on
        blogs = get_posts_pagination(limit, offset)
        lastPage = math.ceil(blogs.count() / limit) #calculate the last page required based on the number of entries and entries displayed per page
        self.render("list.html", blogs=blogs, page=page, lastPage=lastPage, username=username, c=c)

    def get(self):
        page = self.request.get("page") #set url query string
        self.render_list(page)

class NewPost(Handler):
    def render_post(self, title="", body="", error=""):
        self.render("post.html", title=title, body=body, error=error)

    def get(self):
        self.render_post()

    def post(self):
        title = self.request.get("title")
        body = self.request.get("body")

        if title and body:
            post = Blog(title = title, body = body) #create new blog object named post
            post.put() #store post in database
            blogID = "/blog/%s" % str(post.key().id())
            self.redirect(blogID) #send you to view post page
        else:
            error = "Please enter both title and body!"
            self.render_post(title, body, error)

class Archive(Handler):
    def render_archive(self, blogs=""):
        blogs = get_posts() #call get_posts to run GQL query
        self.render("list.html", blogs=blogs)

    def get(self):
        self.render_archive()

class ModifyPost(Handler):
    def render_modify(self, blogs=""):
        blogs = get_posts() #call get_posts to run GQL query
        self.render("modify_post.html", blogs=blogs)

    def get(self):
        self.render_modify()

class ViewPost(Handler):
    def render_view(self, post_id):
        post_id = int(post_id) #post_id is stored as a string initially and will need to be tested against an int in view.html
        post = Blog.get_by_id(post_id)
        self.render("view.html", post=post, post_id=post_id)

    def get(self, post_id):
        self.render_view(post_id)

class EditPost(Handler):
    def render_post(self, post_id, title="", body="", error=""):
        post_id = int(post_id) #post_id is stored as a string initially and will need to be tested against an int in view.html
        post = Blog.get_by_id(post_id) #retrieve row entry from Blog database based on id# in post_id and name it post
        title = post.title #get title of post
        body = post.body #get body of post
        self.render("edit_post.html", post=post, post_id=post_id, title=title, body=body, error=error)

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
            user_id = int(user.key().id())
            self.response.headers.add_header('Set-Cookie', 'user=%s' % make_user_id_hash(user_id)) #hash user id for use in cookie
            self.redirect('/')
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

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/new_post', NewPost),
    ('/archive', Archive),
    ('/modify_post', ModifyPost),
    webapp2.Route('/blog/<post_id:\d+>', ViewPost),
    webapp2.Route('/blog/<post_id:\d+>/edit', EditPost),
    webapp2.Route('/blog/<post_id:\d+>/delete', DeletePost),
    ('/registration', Registration)
], debug=True)
