from google.appengine.ext import db
from google.appengine.api.users import User
from google.appengine.ext import blobstore
import sha



class RealmKeys(db.Model):
    realm_name = db.StringProperty()
    def fetch(self,key):
        result = self.get(key)
        if result:
            return result
        return None

class UploadRequestKeys(db.Model):
    realm_key = db.ReferenceProperty(RealmKeys)
    expire_date = db.DateTimeProperty()

class Image(db.Model):
    "Represents an image stored in the datastore"
    # blog properties storing up to 1MB of binary data
    image = db.BlobProperty()
    thumb = db.BlobProperty()
    original = db.BlobProperty()
    # store the date just in case
    date = db.DateTimeProperty(auto_now_add=True)
    # all images are associated with the user who uploades them
    # this way we can make it a multi user system if that's useful
    user = db.UserProperty()
    #cat = db.ReferenceProperty(Category,collection_name='images')

class File(db.Model):
    "Represents a file stored in the datastore"
    # blog properties storing up to 1MB of binary data
    name = db.TextProperty()
    file = db.BlobProperty()
    content_type = db.TextProperty()
    # store the date just in case
    date = db.DateTimeProperty(auto_now_add=True)
    # all images are associated with the user who uploades them
    # this way we can make it a multi user system if that's useful
    user = db.UserProperty()
    #cat = db.ReferenceProperty(Category,collection_name='cssfiles')

class TemplateFile(db.Model):
    "Represents a file stored in the datastore"
    # blog properties storing up to 1MB of binary data
    name = db.TextProperty()
    file = db.BlobProperty()
    # store the date just in case
    date = db.DateTimeProperty(auto_now_add=True)
    # all images are associated with the user who uploades them
    # this way we can make it a multi user system if that's useful
    user = db.UserProperty()
    #cat = db.ReferenceProperty(Category,collection_name='cssfiles')

class JavascriptFile(db.Model):
    "Represents a file stored in the datastore"
    # blog properties storing up to 1MB of binary data
    name = db.TextProperty()
    file = db.BlobProperty()
    # store the date just in case
    date = db.DateTimeProperty(auto_now_add=True)
    # all images are associated with the user who uploades them
    # this way we can make it a multi user system if that's useful
    user = db.UserProperty()
    #cat = db.ReferenceProperty(Category,collection_name='cssfiles')

class BlobFile(db.Model):
    "Represents a file stored in the datastore"
    name = db.TextProperty()
    blobkey = blobstore.BlobReferenceProperty()
    date = db.DateTimeProperty(auto_now_add=True)
    user = db.UserProperty()
    #cat = db.ReferenceProperty(Category,collection_name='blobfiles')
    