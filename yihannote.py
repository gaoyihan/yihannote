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
    def __init__(self, key, content, type, child_index):
        self.children = []
        self.key = key
        self.content = content
        self.type = type
        self.child_index = child_index
    
def generate_hierarchy(entries):
    key_lookup = {}
    for entry in entries:
        key_lookup[entry.key] = ContentTree(entry.key, entry.content,
                                            entry.type, entry.child_index)
    root_nodes = []
    for entry in entries:
        if (entry.parent_key) and (entry.parent_key in key_lookup):
            key_lookup[entry.parent_key].children.append(key_lookup[entry.key])
        else:
            root_nodes.append(key_lookup[entry.key])
    for k,node in key_lookup.items():
        node.children.sort(key=lambda x:x.child_index)
    root_nodes.sort(key=lambda x:x.child_index)
    return root_nodes
    
def get_latex_content(entry, level):
    latex_content = ''
    if (entry.type == 'title'):
        if level == 1:
            latex_content += '\section{' + entry.content + '}\n'
        elif level == 2:
            latex_content += '\subsection{' + entry.content + '}\n'
        elif level == 3:
            latex_content += '\subsubsection{' + entry.content + '}\n'
    elif (entry.type == 'equation'):
        latex_content += '$$' + entry.content + '$$\n'
    elif (entry.type == 'paragraph'):
        latex_content += entry.content + '\n\n'

    children = datastore.get_child_of_entry(entry.key)
    children.sort(key = lambda x:x.child_index)
    for child in children:
        latex_content += get_latex_content(child, level + 1)
    return latex_content
    
def get_hierarchy_level(key):
    level = 0
    entry = datastore.get_entries([key])[0]
    while (entry):
        entry = datastore.get_entries([entry.parent_key])[0]
        level += 1
    return level

class MainPage(webapp2.RequestHandler):
    def get(self):
        entries = datastore.get_all_entries()
        template_values = {
            'sections': generate_hierarchy(entries)
        }
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))

class NodeInfo(webapp2.RequestHandler):
    def get(self):
        key = self.request.get('key')
        object = datastore.get_entries([key])[0]
        json_object = {
            'key':object.key, 
            'parent_key':object.parent_key, 
            'content':object.content, 
            'child_index':object.child_index,
            'type':object.type
        }
        self.response.write(json.dumps(json_object))
        
class EditEntry(webapp2.RequestHandler):
    def post(self):
        key = self.request.get('key')
        parent_key = self.request.get('parent_key')
        content = self.request.get('content')
        child_index = int(self.request.get('child_index'))
        type = self.request.get('type')
        entry = datastore.Entry(key, parent_key, content, type, child_index)
        datastore.add_or_update_entries([entry])
        self.redirect('/')
        
class LatexContent(webapp2.RequestHandler):
    def get(self):
        key = self.request.get('key')
        level = get_hierarchy_level(key)
        entry = datastore.get_entries([key])[0]
        latex_content = get_latex_content(entry, level)
        self.response.write(latex_content)

class LatexPost(webapp2.RequestHandler):
    def post(self):
        key = self.request.get('key')
        content = self.request.get('content')
        entry = datastore.get_entries([key])[0]
        subtree_keys = get_subtree(key)
        datastore.delete_entries(subtree_keys)

        self.redirect('/')

application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/NodeInfo', NodeInfo),
    ('/EditEntry', EditEntry),
    ('/LatexContent', LatexContent),
    ('/LatexPost', LatexPost)
], debug=True)

datastore.create_test_entries()
