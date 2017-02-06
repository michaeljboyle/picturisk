from google.appengine.ext import ndb
from datetime import datetime

class Record(ndb.Model):
  """A model for representing an odd and its image"""
  title = ndb.StringProperty()
  num = ndb.IntegerProperty()
  denom = ndb.IntegerProperty()
  category = ndb.StringProperty()
  createDate = ndb.DateTimeProperty()
  citation = ndb.StringProperty()
  

  def json(self):
    j = {
      'key': self.key.urlsafe(),
      'title': self.title,
      'odds': str(self.num) + ':' + str(self.denom),
      'citation': self.citation,
      'createDate': str(self.createDate)
    };
    return j

def get_all():
  return Record.query()

def get(urlkey):
  return ndb.Key(urlsafe=urlkey).get()

def new(title, num, denom, citation):
  record = Record()
  record.title = title
  record.num = num
  record.denom = denom
  record.citation = citation
  record.createDate = datetime.now()
  record.put()
  return record

def delete(key):
  ndb.Key(urlsafe=key).delete()
