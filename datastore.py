from google.appengine.ext import ndb
from google.appengine.api import users
import logging

class Entry:
    def __init__(self, key, parent_key, content, type, child_index):
        self.key = key
        self.parent_key = parent_key
        self.content = content
        self.type = type
        self.child_index = child_index

PARENT_KEY = 'yihannote'
NONE_KEY = 'NONE_KEY'

def get_key():
    return ndb.Key('Note', PARENT_KEY)

class DataStoreEntry(ndb.Model):
    parent_key = ndb.StringProperty()
    content = ndb.TextProperty()
    type = ndb.StringProperty()
    child_index = ndb.IntegerProperty()

def get_all_entries():
    entries_query = DataStoreEntry.query(ancestor=get_key())
    result = []
    for entry in entries_query.fetch():
        result.append(Entry(entry.key.id(), entry.parent_key,
                            entry.content, entry.type, entry.child_index))
    return result

def get_child_of_entry(key):
    entries_query = DataStoreEntry.query(DataStoreEntry.parent_key == key,
                                         ancestor=get_key())
    result = []
    for entry in entries_query.fetch():
        result.append(Entry(entry.key.id(), entry.parent_key, entry.content,
                            entry.type, entry.child_index))
    return result

def create_test_entries():
    entry1 = Entry('Sec 1', '', 'First Section', 'title', 1)
    entry2 = Entry('Sec 2', '', 'Second Section', 'title', 2)
    entry3 = Entry('Sec 1.1', 'Sec 1', 'First Subsection', 'title', 2)
    entry4 = Entry('Sec 1.2', 'Sec 1', 'Second Subsection', 'title', 3)
    entry5 = Entry('Sec 2 p1', 'Sec 2', 'first paragraph', 'paragraph', 1)
    entry6 = Entry('Sec 2 p2', 'Sec 2', 'second paragraph', 'paragraph', 2)
    entry7 = Entry('Sec 2 eq3', 'Sec 2', '$$\\int_0^1 x^2 dx = \\frac{1}{3}$$', 'equation', 3)
    entry8 = Entry('Sec 1.1.1', 'Sec 1.1', 'First subsubsection', 'title', 1)
    entry9 = Entry('Sec 1.1.1.1', 'Sec 1.1.1', 'First sub3section', 'title', 1)
    entry10 = Entry('Sec 1.1.1.1.1', 'Sec 1.1.1.1', 'First sub4section', 'title', 1)
    entry11 = Entry('Sec 1.1.1.1.1 p1', 'Sec 1.1.1.1.1', 'sub4section paragraph', 'paragraph', 1)
    entry12 = Entry('Sec 2 ol4', 'Sec 2', '', 'ordered_list', 4)
    entry13 = Entry('Sec 1 ul1', 'Sec 1', '', 'list', 1)
    entry14 = Entry('Sec 2 ol4 li1', 'Sec 2 ol4', '', 'list_item', 1)
    entry15 = Entry('Sec 2 ol4 li2', 'Sec 2 ol4', '', 'list_item', 2)
    entry17 = Entry('Sec 2 ol4 li1 p1', 'Sec 2 ol4 li1', 'list content:', 'paragraph', 1)
    entry18 = Entry('Sec 2 ol4 li1 eq2', 'Sec 2 ol4 li1', '$$x^3+y^3=1$$', 'equation', 2)
    entry16 = Entry('Sec 1 ul1 li1', 'Sec 1 ul1', '', 'list_item', 1)
    entry19 = Entry('Sec 1 ul1 li2', 'Sec 1 ul1', '', 'list_item', 2)
    add_or_update_entries([entry1, entry2, entry3, entry4, entry5, entry6, entry7, entry8, entry9, entry10, entry11])
    add_or_update_entries([entry12, entry13, entry14, entry15, entry16, entry17, entry18, entry19])

def get_key_list(entry_keys):
    key_list = []
    for key in entry_keys:
        if key:
            key_list.append(ndb.Key(DataStoreEntry, key, parent=get_key()))
        else:
            key_list.append(ndb.Key(DataStoreEntry, NONE_KEY))
    return key_list 

def get_entries(entry_keys):
    query_result = ndb.get_multi(get_key_list(entry_keys))
    result = []
    for entry in query_result:
        if entry:
            result.append(Entry(entry.key.id(), entry.parent_key, entry.content,
                            entry.type, entry.child_index))
        else:
            result.append(None)
    return result
    
def delete_entries(entry_keys):
    ndb.delete_multi(get_key_list(entry_keys))
    
def add_or_update_entries(entries):
    data_store_entries = []
    for entry in entries:
        data_store_entry = DataStoreEntry(parent=get_key(), id=entry.key)
        data_store_entry.parent_key = entry.parent_key
        data_store_entry.content = entry.content
        data_store_entry.child_index = entry.child_index
        data_store_entry.type = entry.type
        data_store_entries.append(data_store_entry)
    ndb.put_multi(data_store_entries)
