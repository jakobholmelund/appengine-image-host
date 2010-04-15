"""
Provides a protected administrative area for uploading and deleteing images
"""

import os
import datetime
import logging
import cssmin

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import images
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext import blobstore
from django.utils import simplejson
from urlgetter import geturl

from models import Image,File,BlobFile,RealmKeys,UploadRequestKeys

class Index(webapp.RequestHandler):
    """
    Main view for the application.
    Protected to logged in users only.
    """
    def get(self):
        "Responds to GET requets with the admin interface"
        # query the datastore for images owned by
        # the current user. You can't see anyone elses images
        # in the admin
        '''
        org = Organisation().get_by_name(org)
              
        if org is None:
            return self.error(404)
        
        cats = org.cats
        
        if cats is None:
            return self.error(404)
        
        activeimgcat = self.request.get("imgcat")
        activecsscat = self.request.get("csscat")
        activeblobcat = self.request.get("blobcat")
        
        if activeimgcat is None:
            activeimgcat = org.cats[0]
            activecsscat = org.cats[0]
            activeblobcat = org.cats[0]

        
        
        images = []
        files = []
        blobs = []
        
        for cat in cats:
            images[cat] = cat.images
            files[cat] = cat.cssfiles.filter("user =", user).order("-date")
            blobs[cat] = cat.blobfiles.filter("user =", user).order("-date")            
        '''
        
        test = geturl('http://org-images.appspot.com/remote/upload/image/agpvcmctaW1hZ2VzchALEglSZWFsbUtleXMY0Q8M')
        url = test.get_url()
        
        user = users.get_current_user()
        
        realms = RealmKeys.all()
        
        images = Image.all().filter("user =", user).order("-date")
        
        files = File.all()
        files.filter("user =", user)
        files.order("-date")
        
        blobs = BlobFile.all()
        blobs.filter("user =", user)
        blobs.order("-date")
        
        # we are enforcing loggins so we know we have a user
        
        # we need the logout url for the frontend
        logout = users.create_logout_url("/")

        # prepare the context for the template
        context = {
            "testurl" : url,
            "blobuploadurl" : blobstore.create_upload_url('/upload/blob'),
            "blobs": blobs,
            "files": files,
            "images": images,
            "logout": logout,
            "realms": realms,
        }
        # calculate the template path
        path = os.path.join(os.path.dirname(__file__), 'templates',
            'index.html')
        # render the template with the provided context
        self.response.out.write(template.render(path, context))
    def post(self):
        realm = RealmKeys()
        realm.realm_name = self.request.get("realm_name")
        realm.put()
        self.redirect('/')

class Deleter(webapp.RequestHandler):
    "Deals with deleting images"
    def post(self):
        "Delete a given image"
        # we get the user as you can only delete your own images
        user = users.get_current_user()
        key = self.request.get("key")
        if key:
            object = db.get(key)
            # check that we own this image
            if object.user == user:
                object.delete()
        # whatever happens rediect back to the main admin view
        self.redirect('/')

class ImageUploader(webapp.RequestHandler):
    def post(self):
        "Upload via a multitype POST message"

        img = self.request.get("img")
        # if we don't have image data we'll quit now
        if not img:
            self.redirect('/')
            return
        try:
            width = int(self.request.get("width"))
            hight = int(self.request.get("height"))
        except ValueError:
            image_content = img
        else:
            image_content = images.resize(img, width, height)

        original_content = img

        thumb_content = images.resize(img, 100, 100)

        image = Image()

        image.image = db.Blob(image_content)

        image.original = db.Blob(original_content)
        image.thumb = db.Blob(thumb_content)
        image.user = users.get_current_user()
        image.put()
        self.redirect('/')

class FileUploader(webapp.RequestHandler):
    def post(self):
        fil = self.request.POST["file"]
        if not fil.value:
            self.redirect('/')
            return
        minifi = self.request.get("minify")
        
        if minifi:
            fil.value = cssmin.cssmin(fil.value)
        file = File()
        file.name = fil.filename
        file.file = db.Blob(fil.value)
        file.content_type = fil.type
        file.user = users.get_current_user()
        file.put()
        self.redirect('/')
        
class JscriptUploader(webapp.RequestHandler):
    def post(self):
        fil = self.request.POST["file"]
        if not fil.value:
            self.redirect('/')
            return
        minifi = self.request.get("minify")
        
        if minifi:
            fil.value = cssmin.cssmin(fil.value)
        file = File()
        file.name = fil.filename
        file.file = db.Blob(fil.value)
        file.content_type = fil.type
        file.user = users.get_current_user()
        file.put()
        self.redirect('/')
        
class BlobUploader(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        upload_files = self.get_uploads('file')  # 'file' is file upload field in the form
        blob_info = upload_files[0]
        blobfile = BlobFile()
        blobfile.blobkey = blob_info.key()
        blobfile.name = blob_info.filename
        blobfile.user = users.get_current_user()
        blobfile.put()
        self.redirect('/')

# wire up the views
application = webapp.WSGIApplication([
    ('/', Index),
    ('/upload/image', ImageUploader),
    ('/upload/file', FileUploader),
    ('/upload/blob', BlobUploader),

    ('/delete', Deleter)
], debug=True)

def main():
    "Run the application"
    run_wsgi_app(application)

if __name__ == '__main__':
    main()