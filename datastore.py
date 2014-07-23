from google.appengine.ext import ndb

class Entry:
    def __init__(self, key, parent_key, title, content, has_child, child_index, is_equation):
        self.key = key
        self.parent_key = parent_key
        self.title = title
        self.content = content
        self.has_child = has_child
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
    has_child = ndb.BooleanProperty()
    child_index = ndb.IntegerProperty()
    is_equation = ndb.BooleanProperty()

def get_all_entries():
    return []
    
def get_all_test_entries():
    entry1 = Entry('Sec 1', '', 'First Section', 'first section content', True, 1, False)
    entry2 = Entry('Sec 2', '', 'Second Section', 'second section content', False, 2, False)
    entry3 = Entry('Sec 1.1', 'Sec 1', 'First Subsection', 'first subsection content', False, 1, False)
    entry4 = Entry('Sec 1.2', 'Sec 1', 'Second Subsection', 'second subsection content', False, 2, False)
    return [entry1, entry2, entry3, entry4]

