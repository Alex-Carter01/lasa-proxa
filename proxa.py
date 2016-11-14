import webapp2
import logging
import re
import jinja2
import os
from google.appengine.ext import db
import urllib2

def guess_autoescape(template_name):
    if template_name is None or '.' not in template_name:
        return False
    ext = template_name.rsplit('.', 1)[1]
    return ext in ('html', 'htm', 'xml')

JINJA_ENVIRONMENT = jinja2.Environment(
    autoescape=guess_autoescape,
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'])

WEBSITE_REGEX = re.compile(r"^(http|https)://www[.]")
TREATMENT1 = re.compile(r"^(http|https)")

def valid_url(url):
    logging.info("*** regex match: "+str(bool(WEBSITE_REGEX.match(url))))
    return bool(WEBSITE_REGEX.match(url))

def url_treatment(url):
    if(not bool(TREATMENT1.match(url))):
        url = "http"+url
    return url

class Logs(db.Model):
    website = db.StringProperty()
    ip = db.TextProperty()
    created = db.DateTimeProperty(auto_now_add=True)#date accessed

class MyHandler(webapp2.RequestHandler):
    def write(self, *writeArgs):    
        self.response.write(" : ".join(writeArgs))

    def render_str(self, template, **params):
        tplt = JINJA_ENVIRONMENT.get_template('templates/'+template)
        return tplt.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class MainPage(MyHandler):
    def get(self):
        logging.info("*** MainPage GET ")
        form = JINJA_ENVIRONMENT.get_template('templates/form.html')
        self.write(form.render())

    def post(self):#this should return a site mirror
        logging.info("*** Enter Post")
        form = JINJA_ENVIRONMENT.get_template('templates/form.html')
        web = self.request.get("website")
        logging.info("user attempted to access: "+web)
        ip = self.request.remote_addr
        log = Logs()
        log.website = web
        log.ip = ip
        log.put()
        web = url_treatment(web)
        if(not valid_url(web)):
            error_v = {"error": "Error: that is not a valid website url"}
            self.write(form.render(error_v))
        else:
            #self.write("legit")
            response = urllib2.urlopen(web)
            html = response.read()
            #response = urllib2.urlopen(web)
            #html = response.read()
            #logging.info("html: "+html)
            self.write(html)


class Terms(MyHandler):
    def get(self):
        logging.info("*** lol someone actually went to the legal part")
        terms = JINJA_ENVIRONMENT.get_template('templates/terms.html')
        self.write(terms.render())

application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/terms', Terms),
], debug=True)
