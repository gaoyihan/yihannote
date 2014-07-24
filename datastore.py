from google.appengine.ext import ndb
import logging

class Entry:
    def __init__(self, key, parent_key, title, content, child_index, is_equation):
        self.key = key
        self.parent_key = parent_key
        self.title = title
        self.content = content
        self.child_index = child_index
        self.is_equation = is_equation

PARENT_KEY = 'yihannote'

def get_key():
    return ndb.Key('Note', PARENT_KEY)

class DataStoreEntry(ndb.Model):
    key = ndb.StringProperty()
    parent_key = ndb.StringProperty()
    title = ndb.StringProperty(indexed=False)
    content = ndb.TextProperty()
    child_index = ndb.IntegerProperty()
    is_equation = ndb.BooleanProperty()

def get_all_entries():
    return []
    
def get_all_test_entries():
    entry1 = Entry('Sec 1', '', 'First Section', 'first section content', 1, False)
    entry2 = Entry('Sec 2', '', 'Second Section', 'second section content', 2, False)
    entry3 = Entry('Sec 1.1', 'Sec 1', 'First Subsection', 'first subsection content', 1, False)
    entry4 = Entry('Sec 1.2', 'Sec 1', 'Second Subsection', 'second subsection content', 2, False)
    entry5 = Entry('Sec 2 p2', 'Sec 2', '', 'second paragraph', 1, False)
    entry6 = Entry('Sec 2 eq1', 'Sec 2', '', '\\int_0^1 x^2 dx = \\frac{1}{3}', 2, True)
    return [entry1, entry2, entry3, entry4, entry5, entry6]

def get_entries(entry_keys):
    return [Entry(entry_keys[0], 'test_parent', 'test_title', 'test_content', 1, False)]

def delete_entries(entry_keys):
    pass
    
def add_entries(entries):
    pass
