import os, webapp2, math, re, json #import stock python methods (re is regular expersions)
import jinja2 #need to install jinja2 (not stock)
import hashing, gqlqueries, validuser, coordinateRetrieval, caching #import python files I've made
from dbmodels import Users, Blog #import Users and Blog classes from python file named dbmodels
import time

#setup jinja2
template_dir = os.path.join(os.path.dirname(__file__), 'templates') #set template_dir to main.py dir(current dir)/templates
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True) #set jinja2's working directory to template_dir

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
            uid = hashing.check_secure_val(c)

        self.user = uid and Users.get_by_id(int(uid))

        if not self.user and self.request.path in auth_paths:
            self.redirect('/login')

class PostList(Handler): # if u has value then posts will be displayed by user, else all posts are displayed
    limit = 5 #number of entries displayed per page

    def render_list(self, u, page="", blogs=""):
        c = self.request.cookies.get('user') #pull cookie value
        usr = hashing.get_user_from_cookie(c)
        if u:
            poster = caching.cached_user_by_name(u) #pulls the user from the db by name passed through the url
        else:
            poster = ""

        page = self.request.get("page") #pull url query string
        if not page:
            page = 1
        else:
            page = int(page)
        offset = (page - 1) * 5 #calculate where to start offset based on which page the user is on

        blogs = caching.cached_posts(self.limit, offset, poster)
        allPosts = caching.cached_posts(None, 0, poster)
        lastPage = math.ceil(len(allPosts) / float(self.limit)) #calculate the last page required based on the number of entries and entries displayed per page
        self.render("list.html", blogs=blogs, page=page, lastPage=lastPage, usr=usr, u=u)

    def get(self, u=""):
        page = self.request.get("page") #set url query string
        if u:
            self.render_list(u, page)
        else:
            self.render_list(None, page)

class Archive(Handler):
    def render_archive(self, blogs=""):
        c = self.request.cookies.get('user') #pull cookie value
        usr = hashing.get_user_from_cookie(c)

        blogs = caching.cached_posts() #call get_posts to run GQL query
        self.render("list.html", blogs=blogs, usr=usr)

    def get(self):
        self.render_archive()

class NewPost(Handler):
    def render_post(self, title="", body="", error=""):
        c = self.request.cookies.get('user') #pull cookie value
        usr = hashing.get_user_from_cookie(c)
        self.render("post.html", title=title, body=body, error=error, usr=usr)

    def get(self):
        self.render_post()

    def post(self):
        c = self.request.cookies.get('user') #pull cookie value
        usr = hashing.get_user_from_cookie(c)

        title = self.request.get("title")
        body = self.request.get("body")

        if title and body:
            post = Blog(title = title, body = body, author = self.user) #create new blog object named post
            coords = coordinateRetrieval.get_coords(self.request.remote_addr) #pull coordinates based on IP of poster
            if coords:
                post.coords = coords #if we have coordinates, add them to the db entry
            post.put() #store post in database

            """cache updating"""
            #update cache
            time.sleep(.1) #ewait 1/10 of a second while post is entered into db
            poster = caching.cached_user_by_name(post.author.username) #pulls the user from the db by name passed through the url
            caching.cached_posts(None, 0, poster, True) #direct cached_posts to update cache
            caching.cached_posts(None, 0, "", True) #direct cached_posts to update cache

            limit = PostList.limit #number of entries displayed per page

            #update cache of pagination by user
            allPostsByPoster = caching.cached_posts(None, 0, poster)
            lastPageByPoster = math.ceil(len(allPostsByPoster) / float(limit)) #calculate the last page required based on the number of entries and entries displayed per page

            for i in range(int(lastPageByPoster), 0, -1):
                offset = (i - 1) * 5
                caching.cached_posts(limit, offset, poster, True) #direct cached_posts to update cache

            #update cache of pagination for all posts
            allPosts = caching.cached_posts(None, 0, "")
            lastPage = math.ceil(len(allPosts) / float(limit)) #calculate the last page required based on the number of entries and entries displayed per page

            for i in range(int(lastPage), 0, -1):
                offset = (i - 1) * 5
                caching.cached_posts(limit, offset, "", True) #direct cached_posts to update cache
            """end of cache updating"""

            blogID = "/post/%s" % str(post.key().id())
            self.redirect(blogID) #send you to view post page
        else:
            error = "Please enter both title and body!"
            self.render_post(title, body, error)

class ModifyPost(Handler):
    def render_modify(self, blogs=""):
        c = self.request.cookies.get('user') #pull cookie value
        usr = hashing.get_user_from_cookie(c)
        poster = caching.cached_user_by_name(usr) #pulls the user from the db by name passed through the url
        blogs = caching.cached_posts(None, 0, poster) #call get_posts to run GQL query
        self.render("modify_post.html", blogs=blogs, usr=usr)

    def get(self):
        self.render_modify()

class ViewPost(Handler):
    def render_view(self, post_id):
        c = self.request.cookies.get('user') #pull cookie value
        usr = hashing.get_user_from_cookie(c)

        post_id = int(post_id) #post_id is stored as a string initially and will need to be tested against an int in view.html
        post = Blog.get_by_id(post_id)
        self.render("view.html", post=post, post_id=post_id, usr=usr)

    def get(self, post_id):
        self.render_view(post_id)

class EditPost(Handler):
    def render_post(self, post_id, title="", body="", error=""):
        c = self.request.cookies.get('user') #pull cookie value
        usr = hashing.get_user_from_cookie(c)
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
            blogID = "/post/%s" % str(post_id)
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
        elif not validuser.valid_password(password): #check if password is valid
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
        elif not validuser.valid_username(username): #check if username if valid
            usernameError = "Invalid Username"
            error = True
        elif caching.cached_check_username(username): #check if username is unique
            usernameError = "That username is taken"
            error = True
        else:
            usernameError = ""
        #check email
        if not email: #check if email is blank
            emailError = ""
        elif not validuser.valid_email(email): #check if email is valid
            emailError = "Invalid Email"
            error = True
        else:
            emailError = ""
        #see if any errors returned
        if error == False:
            username = username
            password = hashing.make_pw_hash(username, password) #hash password for storage in db
            user = Users(username=username, password=password, email=email) #create new blog object named post
            user.put() #store post in database
            user_id = user.key().id()
            self.response.headers.add_header('Set-Cookie', 'user=%s' % hashing.make_secure_val(user_id)) #hash user id for use in cookie
            caching.cached_user_by_name(username, True) #direct cached_posts to update cache
            caching.cached_check_username(username, True) #direct cached_posts to update cache
            self.redirect('/welcome')
        else:
            self.render_reg(username, email, usernameError, passwordError, passVerifyError, emailError)

class Login(Handler):
    def render_login(self, username="", error=""):
        self.render("login.html", username=username, error=error)

    def get(self):
        self.render_login()

    def post(self):
        username = self.request.get("username")
        password = self.request.get("password")

        if not caching.cached_check_username(username):
            error = "Invalid login"
        else:
            user_id = caching.cached_check_username(username)
            user_id = int(user_id)
            u = Users.get_by_id(user_id)
            p = u.password
            salt = p.split("|")[1]
            if username == u.username:
                if hashing.make_pw_hash(username, password, salt) == p:
                    error = ""
                else:
                    error = "invalid login - pass"

        if error:
            self.render_login(username, error)
        else:
            self.response.headers.add_header('Set-Cookie', 'user=%s' % hashing.make_secure_val(user_id)) #hash user id for use in cookie
            self.redirect('/welcome')

class Logout(Handler):
    def get(self):
        self.response.headers.add_header('Set-Cookie', 'user=""; expires=Thu, 01-Jan-1970 00:00:10 GMT') #clear cookie
        self.redirect('/registration')

class Welcome(Handler):
    def render_welcome(self):
        c = self.request.cookies.get('user') #pull cookie value
        usr = hashing.get_user_from_cookie(c)

        self.redirect('/')

    def get(self):
        self.render_welcome()

class Map(Handler):
    def render_map(self):
        c = self.request.cookies.get('user') #pull cookie value
        usr = hashing.get_user_from_cookie(c)

        blogs = caching.cached_posts()
        # arts = list(arts) #turns the db query above into a list object so that it doesnt run a new db search each time it is called

        points = []
        for b in blogs: #find which arts have coords
            points.append(b.coords) #if we have any arts coords, make an image url

        mapUrl = coordinateRetrieval.getMap(points)

        self.render("map.html", usr=usr, mapUrl=mapUrl)

    def get(self):
        self.render_map()

class jsonHandler(Handler):
    def render_json(self, post_id=""):
        if post_id: #if a single post is requested fetch by ID
            post_id = int(post_id) #post_id is stored as a string initially and will need to be tested against an int in view.html
            post = Blog.get_by_id(post_id)
            jsonData = {} #establish reusable blogData dictionary
            jsonData["title"] = post.title #add title to dictionary
            jsonData["body"] = post.body #add body to dictionary
            jsonData["created"] = post.created.strftime('%m.%d.%Y') #add created date to dictionary and format
            jsonData["last_modified"] = post.last_modified.strftime('%m.%d.%Y') #add modified date to dictionary and format
            jsonData["author"] = post.author.username #add author to dictionary
        else: #if entire blog is requested iterate through database
            jsonData = [] #establish jsonData list
            blogs = caching.cached_posts() #call get_posts to run GQL query
            for b in blogs:
                blogData = {} #establish reusable blogData dictionary
                blogData["title"] = b.title #add title to dictionary
                blogData["body"] = b.body #add body to dictionary
                blogData["created"] = b.created.strftime('%m.%d.%Y') #add created date to dictionary and format
                blogData["last_modified"] = b.last_modified.strftime('%m.%d.%Y') #add modified date to dictionary and format
                blogData["author"] = b.author.username #add author to dictionary
                jsonData.append(blogData) #add dictionary to list
        self.response.headers['Content-Type'] = 'application/json; charset=UTF-8' #set content-type to json and charset to UTF-8
        self.write(json.dumps(jsonData)) #write json data to page

    def get(self, post_id=""):
        self.render_json(post_id)

app = webapp2.WSGIApplication([
    ('/', PostList),
    webapp2.Route('/user/<u:[a-zA-Z0-9_-]{3,20}>', PostList),
    ('/archive/?', Archive),
    ('/new_post/?', NewPost),
    ('/modify_post/?', ModifyPost),
    webapp2.Route('/post/<post_id:\d+>', ViewPost),
    webapp2.Route('/post/<post_id:\d+>/edit', EditPost),
    webapp2.Route('/post/<post_id:\d+>/delete', DeletePost),
    ('/registration/?', Registration),
    ('/login/?', Login),
    ('/logout/?', Logout),
    ('/welcome/?', Welcome),
    ('/map/?', Map),
    ('/.json', jsonHandler),
    webapp2.Route('/post/<post_id:\d+>.json', jsonHandler)
], debug=True)

auth_paths = [ #must be logged in to access these links
    '/new_post',
    '/new_post/',
    '/modify_post',
    '/modify_post/',
    '/post/<post_id:\d+>/edit',
    '/post/<post_id:\d+>/delete'
]
