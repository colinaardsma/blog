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

class MainPage(Handler):
    def render_list(self, blogs=""):
        blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC LIMIT 5") #table is named Blog because class is named Blog (the class creates the table)
        self.render("list.html", blogs=blogs)

    def get(self):
        self.render_list()

class NewPost(Handler):
    def render_post(self, title="", body="", error=""):
        self.render("new_post.html", title=title, body=body, error=error)

    def get(self):
        self.render_post()

    def post(self):
        title = self.request.get("title")
        body = self.request.get("body")

        if title and body:
            a = Blog(title = title, body = body) #creates new blog object named a
            a.put() #stores a in database
            self.redirect('/') #sends you back to new post page
        else:
            error = "Please enter both title and body!"
            self.render_post(title, body, error)

class Archive(Handler):
    def render_list(self, blogs=""):
        blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC") #table is named Blog because class is named Blog (the class creates the table)
        self.render("list.html", blogs=blogs)

    def get(self):
        self.render_list()

class DeletePost(Handler):
    def render_delete(self, blogs=""):
        blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC") #table is named Blog because class is named Blog (the class creates the table)
        self.render("delete_post.html", blogs=blogs)

    def get(self):
        self.render_delete()

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/new_post', NewPost),
    ('/archive', Archive),
    ('/delete_post', DeletePost)
], debug=True)
