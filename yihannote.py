import logging
import json
import os
import urllib

from google.appengine.api import users
from google.appengine.ext import db

import jinja2
import webapp2

import datastore
import latex

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class ContentTree:
    def __init__(self, key, content, type, child_index):
        self.children = []
        self.parts = []
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

def parse_paragraph(content):
    if '\\textbf{' in content:
        start_index = content.find('\\textbf{')
        end_index = content.find('}', start_index)
        first_half = parse_paragraph(content[:start_index])
        second_half = parse_paragraph(content[end_index + 1:])
        mid = ContentTree('', content[start_index + len('\\textbf{'):end_index], 'bold', 0)
        return first_half + [mid] + second_half
    elif '\\href{' in content:
        start_index = content.find('\\href{')
        end_first_param = content.find('}{', start_index)
        end_index = content.find('}', end_first_param + 2)
        first_half = parse_paragraph(content[:start_index])
        second_half = parse_paragraph(content[end_index + 1:])
        mid = ContentTree('', content[end_first_param + len('}{'):end_index], 'anchor', 0)
        mid.href = content[start_index + len('\\href{'):end_first_param]
        if mid.href[0] == '.':
            mid.href = mid.href[1:]
        return first_half + [mid] + second_half
    elif '\\hyperref[' in content:
        start_index = content.find('\\hyperref[')
        end_first_param = content.find(']{', start_index)
        end_index = content.find('}', end_first_param + 2)
        first_half = parse_paragraph(content[:start_index])
        second_half = parse_paragraph(content[end_index + 1:])
        mid = ContentTree('', content[end_first_param + len(']{'):end_index], 'anchor', 0)
        mid.href = content[start_index + len('\\hyperref['):end_first_param]
        mid.href = '#' + mid.href
        return first_half + [mid] + second_half
    else:
        return [ContentTree('', content, 'text', 0)]

def post_process(sections):
    for section in sections:
        if section.type == 'paragraph':
            parsed_paragraph = parse_paragraph(section.content)
            section.parts += parsed_paragraph
        else:
            post_process(section.children)

def get_subtree(key):
    children = datastore.get_child_of_entry(key)
    list = [datastore.get_entries([key])[0].key]
    for child in children:
        subtree = get_subtree(child.key)
        list += subtree
    return list
    
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
        # Get User Information, Generate Welcome Message, Display edit page if user is admin
        user = users.get_current_user()
        allow_modification = False
        if user:
            login_logout_message = ('Welcome, %s!' % user.nickname())
            login_logout_url = users.create_logout_url('/')
            login_logout_linktext = 'Sign out'
            if users.is_current_user_admin():
                allow_modification = True
        else:
            login_logout_message = 'Welcome, guest!'
            login_logout_url = users.create_login_url('/')
            login_logout_linktext = 'Sign in or register'
        # Render the template
        sections = generate_hierarchy(entries)
        post_process(sections)
        template_values = {
            'sections': sections,
            'login_logout_message': login_logout_message,
            'login_logout_url': login_logout_url,
            'login_logout_linktext': login_logout_linktext,
            'allow_modification': allow_modification
        }
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))

class NodeInfo(webapp2.RequestHandler):
    def get(self):
        key = self.request.get('key')
        if key == 'noteBody':
            node = datastore.Entry('noteBody', '', 'Note Body', 'title', 1)
            children = datastore.get_child_of_entry('')
        else:
            node = datastore.get_entries([key])[0]
            children = datastore.get_child_of_entry(key)
        def to_dict(node):
            return {
                'key': node.key,
                'parent_key': node.parent_key,
                'type': node.type,
                'child_index': node.child_index,
                'content': node.content
            }
        json_object = {
            'node': to_dict(node), 
            'children': map(to_dict, children)
        }
        self.response.write(json.dumps(json_object))

class EditEntry(webapp2.RequestHandler):
    @db.transactional
    def post(self):
        if not users.is_current_user_admin():
            self.redirect('/')
        nodes = json.loads(self.request.body)
        # We need this key set to find implicitly updated subtrees
        old_key_set = set()
        for node in nodes:
            old_key_set.add(node['old_key'])

        update_list = []
        delete_list = []
        for node in nodes:
            old_key = node['old_key']
            if old_key == 'noteBody':
                continue
            key = node['key']
            children = datastore.get_child_of_entry(old_key)
            for child in children:
                if child.key not in old_key_set:
                    subtree = get_subtree(child.key)
                    if node['deleted']:
                        delete_list += subtree
                    elif key != old_key:
                        delete_list += subtree
                        subtree_entries = datastore.get_entries(subtree)
                        prefix_len = len(old_key)
                        for entry in subtree_entries:
                            entry.key = key + entry.key[prefix_len:]
                            entry.parent_key = key + entry.parent_key[prefix_len:]
                        update_list += subtree_entries
            if node['deleted']:
                delete_list.append(old_key)
            else:
                if old_key != 'new_key' and old_key != key:
                    delete_list.append(old_key)
                parent_key = node['parent_key']
                content = node['content']
                type = node['type']
                child_index = node['child_index']
                entry = datastore.Entry(key, parent_key, content, type, child_index)
                update_list.append(entry)

        # It is necessary to delete first because the new keys 
        # might be identical to deleted old_keys
        datastore.delete_entries(delete_list)
        datastore.add_or_update_entries(update_list)

class LatexContent(webapp2.RequestHandler):
    def get(self):
        key = self.request.get('key')
        entry = datastore.get_entries([key])[0]
        level = get_hierarchy_level(entry.key)
        latex_content = latex.get_latex_content(entry, level)
        json_object = {
            'key':entry.key,
            'content':latex_content
        }
        self.response.write(json.dumps(json_object))

class LatexPost(webapp2.RequestHandler):
    @db.transactional
    def post(self):
        if not users.is_current_user_admin():
            self.redirect('/')
        key = self.request.get('key')
        content = self.request.get('content')
        root_entry = datastore.get_entries([key])[0]
        subtree_keys = get_subtree(key)
        datastore.delete_entries(subtree_keys[1:])
        parsed_entries = latex.parse_latex_content(content.splitlines(), root_entry.key)
        datastore.add_or_update_entries(parsed_entries)
        self.redirect('/')

application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/NodeInfo', NodeInfo),
    ('/EditEntry', EditEntry),
    ('/LatexContent', LatexContent),
    ('/LatexPost', LatexPost)
], debug=True)

# For Debugging
#datastore.create_test_entries()
