import os
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Blog(db.Model):
    title = db.StringProperty(required = True) #sets title to a string and makes it required
    body = db.TextProperty(required = True) #sets title to a text and makes it required (text is same as string but can be more than 500 characters and cannot be indexed)
    created = db.DateTimeProperty(auto_now_add = True) #sets created to equal current date/time
    last_modified = db.DateTimeProperty(auto_now = True) #sets last_modified to equal current date/time

class MainPage(Handler):
    def render_list(self, blogs=""):
        blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC LIMIT 5") #table is named Blog because class is named Blog (the class creates the table)
        self.render("list.html", blogs=blogs)

    def get(self):
        self.render_list()

class NewPost(Handler):
    def render_post(self, title="", body="", error=""):
        self.render("post.html", title=title, body=body, error=error)

    def get(self):
        self.render_post()

    def post(self):
        title = self.request.get("title")
        body = self.request.get("body")

        if title and body:
            a = Blog(title = title, body = body) #creates new blog object named a
            a.put() #stores a in database
            blogID = "/blog/%s" % str(a.key().id())
            self.redirect(blogID) #sends you to view post page
        else:
            error = "Please enter both title and body!"
            self.render_post(title, body, error)

class Archive(Handler):
    def render_archive(self, blogs=""):
        blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC") #table is named Blog because class is named Blog (the class creates the table)
        self.render("list.html", blogs=blogs)

    def get(self):
        self.render_archive()

class ModifyPost(Handler):
    def render_modify(self, blogs=""):
        blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC") #table is named Blog because class is named Blog (the class creates the table)
        self.render("modify_post.html", blogs=blogs)

    def get(self):
        self.render_modify()

class ViewPost(Handler):
    def render_view(self, id):
        id = int(id) #id is stored as a string initially and will need to be tested against an int in view.html
        post = Blog.get_by_id(id)
        self.render("view.html", post=post, id=id)

    def get(self, id):
        self.render_view(id)

class EditPost(Handler):
    def render_post(self, id, title="", body="", error=""):
        id = int(id) #id is stored as a string initially and will need to be tested against an int in view.html
        post = Blog.get_by_id(id)
        title = post.title
        body = post.body
        self.render("edit_post.html", post=post, id=id, title=title, body=body, error=error)

    def get(self, id):
        self.render_post(id)

    def post(self, id, title="", body="", error=""):
        title = self.request.get("title")
        body = self.request.get("body")

        if title and body:
            blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC") #table is named Blog because class is named Blog (the class creates the table)
            id = int(id) #id is stored as a string initially and will need to be tested against an int in view.html
            for blog in blogs:
                if blog.key().id() == id:
                    blog.title = title #edits
                    blog.body = body
                    blog.put() #stores a in database
            blogID = "/blog/%s" % str(id)
            self.redirect(blogID) #sends you to view post page
        else:
            error = "Please enter both title and body!"
            self.render_post(id, title, body, error)

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/new_post', NewPost),
    ('/archive', Archive),
    ('/modify_post', ModifyPost),
    webapp2.Route('/blog/<id:\d+>', ViewPost),
    webapp2.Route('/blog/<id:\d+>/edit', EditPost)
], debug=True)
