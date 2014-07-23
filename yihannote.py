import os
import urllib

from google.appengine.api import users

import jinja2
import webapp2

import datastore

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class ContentTree:
    def __init__(self, title, content, is_equation, child_index):
        self.children = []
        self.title = title
        self.content = content
        self.is_equation = is_equation
        self.child_index = child_index
    
def generate_hierarchy(entries):
    key_lookup = {}
    for entry in entries:
        key_lookup[entry.key] = ContentTree(entry.title, entry.content, entry.is_equation, entry.child_index)
    root_nodes = []
    for entry in entries:
        if entry.parent_key:
            key_lookup[entry.parent_key].children.append(key_lookup[entry.key])
        else:
            root_nodes.append(key_lookup[entry.key])
    for k,node in key_lookup.items():
        node.children.sort(key=lambda x:x.child_index)
    return root_nodes
        

class MainPage(webapp2.RequestHandler):
    def get(self):
        entries = datastore.get_all_test_entries()
        template_values = {
            'sections': generate_hierarchy(entries)
        }
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))

application = webapp2.WSGIApplication([
    ('/', MainPage),
], debug=True)

