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

def get_subtree(key):
    children = datastore.get_child_of_entry(key)
    list = [datastore.get_entries([key])[0].key]
    for child in children:
        subtree = get_subtree(child.key)
        list += subtree
    return list
    
def get_latex_content(entry, level):
    latex_content = ''
    children = datastore.get_child_of_entry(entry.key)
    children.sort(key = lambda x:x.child_index)
    for entry in children:
        if (entry.type == 'title'):
            if level == 1:
                latex_content += '\subsection{' + entry.content + '}\n'
            elif level == 2:
                latex_content += '\subsubsection{' + entry.content + '}\n'
            elif level == 3:
                latex_content += '\paragraph{' + entry.content + '}\n'
            elif level == 4:
                latex_content += '\subparagraph{' + entry.content + '}\n'
        elif (entry.type == 'equation'):
            latex_content += entry.content + '\n\n'
        elif (entry.type == 'paragraph'):
            latex_content += entry.content + '\n\n'
        latex_content += get_latex_content(entry, level + 1)
    return latex_content
    
def get_hierarchy_level(key):
    level = 0
    entry = datastore.get_entries([key])[0]
    while (entry):
        entry = datastore.get_entries([entry.parent_key])[0]
        level += 1
    return level

def get_parse_point(content, parse_prefix):
    list = []
    for i in range(0, len(content)):
        if content[i][0:len(parse_prefix)] == parse_prefix:
            list.append(i)
    return list

def str_strip(content, prefix, end_mark):
    end_index = content.index(end_mark)
    return content[len(prefix):end_index]

def set_child_index(list, root_key):
    child_index = 1
    for entry in list:
        if entry.parent_key == root_key:
            entry.child_index = child_index
            child_index += 1

def create_latex_node(content, root_key):
    if len(content) == 0:
        return None
    is_equation = False
    equation_indicator = ['$$', '\\[', '\\begin{equation', '\\begin{align']
    for line in content:
        for indicator in equation_indicator:
            if indicator in line:
                is_equation = True
    if is_equation:
        return datastore.Entry(root_key + ' eq', root_key, '\n'.join(content), 'equation', 0)
    else:
        return datastore.Entry(root_key + ' p', root_key, '\n'.join(content), 'paragraph', 0)

def parse_latex_content(content, root_key):
    if len(content) == 0:
        return []
    prefix_list = ['\\section{', '\\subsection{', '\\subsubsection{', 
                   '\\paragraph{', '\\subparagraph{']
    for prefix in prefix_list:
        sec_list = get_parse_point(content, prefix)
        if len(sec_list) > 0:        
            entry_list = []
            entry_list += parse_latex_content(content[0:sec_list[0]], root_key)
            for i in range(0, len(sec_list)):
                sec_entry = datastore.Entry(root_key + '.' + str(i + 1), root_key, 
                                            str_strip(content[sec_list[i]], prefix, '}'),
                                            'title', 0)
                entry_list.append(sec_entry)
                if i == len(sec_list) - 1:
                    content_sublist = content[sec_list[i] + 1:]
                else:
                    content_sublist = content[sec_list[i] + 1:sec_list[i + 1]]
                entry_list += parse_latex_content(content_sublist, sec_entry.key)
            set_child_index(entry_list, root_key)
            return entry_list
    sec_list = []
    for i in range(0, len(content)):
        if content[i] == '':
            sec_list.append(i)
    if len(sec_list) > 0:
        entry_list = []
        new_node = create_latex_node(content[0:sec_list[0]], root_key)
        if new_node != None:
            entry_list.append(new_node)
        print sec_list, content
        for i in range(0, len(sec_list)):
            if i == len(sec_list) - 1:
                new_node = create_latex_node(content[sec_list[i] + 1:], root_key)
            else:
                new_node = create_latex_node(content[sec_list[i] + 1:sec_list[i + 1]], root_key)
            if new_node != None:
                entry_list.append(new_node)
        set_child_index(entry_list, root_key)
        for entry in entry_list:
            entry.key += str(entry.child_index)
        return entry_list
    else:
        new_node = create_latex_node(content, root_key)
        if new_node != None:
            new_node.key += '1'
            new_node.child_index = 1
            return [new_node]
        else:
            return []

class MainPage(webapp2.RequestHandler):
    def get(self):
        entries = datastore.get_all_entries()
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
        template_values = {
            'sections': generate_hierarchy(entries),
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
        entry = datastore.get_entries([key])[0]
        if entry.type != 'title':
            entry = datastore.get_entries([entry.parent_key])[0]
        level = get_hierarchy_level(entry.key)
        latex_content = get_latex_content(entry, level)
        json_object = {
            'key':entry.key,
            'content':latex_content
        }
        self.response.write(json.dumps(json_object))

class LatexPost(webapp2.RequestHandler):
    def post(self):
        key = self.request.get('key')
        content = self.request.get('content')
        root_entry = datastore.get_entries([key])[0]
        subtree_keys = get_subtree(key)
        #print subtree_keys
        datastore.delete_entries(subtree_keys[1:])
        parsed_entries = parse_latex_content(content.splitlines(), root_entry.key)
        set_child_index(parsed_entries, root_entry.key)
        datastore.add_or_update_entries(parsed_entries)
        #print parsed_entries[0].key, root_entry.child_index
        self.redirect('/')

application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/NodeInfo', NodeInfo),
    ('/EditEntry', EditEntry),
    ('/LatexContent', LatexContent),
    ('/LatexPost', LatexPost)
], debug=True)

#datastore.create_test_entries()
