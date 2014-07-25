import logging
import json
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
    def __init__(self, title, key, content, is_equation, child_index):
        self.children = []
        self.key = key
        self.title = title
        self.content = content
        self.is_equation = is_equation
        self.child_index = child_index
    
def generate_hierarchy(entries):
    key_lookup = {}
    for entry in entries:
        key_lookup[entry.key] = ContentTree(entry.title, entry.key, entry.content,
                                            entry.is_equation, entry.child_index)
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

class NodeInfo(webapp2.RequestHandler):
    def get(self):
        key = self.request.get('key')
        logging.info('Request NodeInfo Key=' + key)
        object = datastore.get_entries([key])[0]
        json_object = {
            'key':object.key, 
            'parent_key':object.parent_key, 
            'title':object.title,
            'content':object.content, 
            'child_index':object.child_index, 
            'is_equation':object.is_equation
        }
        self.response.write(json.dumps(json_object))
        
class EditEntry(webapp2.RequestHandler):
    def post(self):
        key = self.request.get('key')
        parent_key = self.request.get('parent_key')
        title = self.request.get('title')
        content = self.request.get('content')
        child_index = int(self.request.get('child_index'))
        is_equation = bool(self.request.get('is_equation'))
        logging.info('Edit Request {} {} {} {} {} {}'.format(
                     key, parent_key, title, content, child_index, is_equation))
        self.redirect('/')

application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/NodeInfo', NodeInfo),
    ('/EditEntry', EditEntry),
], debug=True)

