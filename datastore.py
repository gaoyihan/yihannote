from google.appengine.ext import ndb
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
    entry3 = Entry('Sec 1.1', 'Sec 1', 'First Subsection', 'title', 1)
    entry4 = Entry('Sec 1.2', 'Sec 1', 'Second Subsection', 'title', 2)
    entry5 = Entry('Sec 2 p1', 'Sec 2', 'first paragraph', 'paragraph', 1)
    entry6 = Entry('Sec 2 p2', 'Sec 2', 'second paragraph', 'paragraph', 2)
    entry7 = Entry('Sec 2 eq1', 'Sec 2', '\\int_0^1 x^2 dx = \\frac{1}{3}', 'equation', 3)
    add_or_update_entries([entry1, entry2, entry3, entry4, entry5, entry6, entry7])

def get_entries(entry_keys):
    key_list = []
    for key in entry_keys:
        if key:
            key_list.append(ndb.Key(DataStoreEntry, key, parent=get_key()))
        else:
            key_list.append(ndb.Key(DataStoreEntry, NONE_KEY))
    query_result = ndb.get_multi(key_list)
    result = []
    for entry in query_result:
        if entry:
            result.append(Entry(entry.key.id(), entry.parent_key, entry.content,
                            entry.type, entry.child_index))
        else:
            result.append(None)
    return result
    
def delete_entries(entry_keys):
    pass
    
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
