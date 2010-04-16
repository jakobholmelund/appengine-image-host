"""
Frontend for the image host. This does the actual serving of the images
for use on others sites and within the admin
"""

import os
import datetime
import logging

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext import blobstore
from django.utils import simplejson
from django.http import HttpResponse
from google.appengine.ext.webapp import template
from google.appengine.api import images
from google.appengine.api import users
import urllib
import cssmin

from models import Image,File,BlobFile,RealmKeys,UploadRequestKeys
  
class GenericServer(webapp.RequestHandler):
    """
    Image server designed to handle serving png images from
    different object properties
    """
    property = 'image'

    def get(self):
        # key is provided in the query string
        key = self.request.get("id")
        try:
            # it might be an invalid key so we better check

            object = db.get(key)
            
        except db.BadKeyError:
            # if it is then return a 404

            self.error(404)
            return
        
        logging.getLogger().info('prop %s'%self.property)
        
        if self.property =='css':
            if object and object.file:
                file = object.file
                
                compress = self.request.get("compress")
                if compress == 'true':
                    file = cssmin.cssmin(file)
                # we have an file so prepare the response
                # with the relevant headers
                
                self.response.headers['Content-Type'] = "text/css"
                # and then write our the image data direct to the response
                self.response.out.write(file)    
            else:
                self.error(404)
        elif self.property =='jscript':
            if object and object.file:
                file = object.file
                # we have an file so prepare the response
                # with the relevant headers
                self.response.headers['Content-Type'] = "text/javascript"
                # and then write our the image data direct to the response
                self.response.out.write(file)    
            else:
                self.error(404)
        elif self.property == 'image' or self.property=='thumb':
            if object and object.image:
                # we have an image so prepare the response
                # with the relevant headers
                self.response.headers['Content-Type'] = "image/png"
                # and then write our the image data direct to the response
                self.response.out.write(eval("object.%s" % self.property))
            else:
                self.error(404)
                
class CSSServer(GenericServer):
    "Serve a File"
    property = 'css'

class JScriptServer(GenericServer):
    "Serve a File"
    property = 'jscript'

class ImageServer(GenericServer):
    "Serve the main image"
    property = 'image'

class ThumbServer(GenericServer):
    "Serve the thumbnail image"
    property = 'thumb'
    
class BlobServer(blobstore_handlers.BlobstoreDownloadHandler):
    "Serve the thumbnail image"
    def get(self):
        key = self.request.get("id")
        try:
            object = db.get(key)
        except db.BadKeyError:
            self.error(404)
            return
        blob_info = object.blobkey
        self.send_blob(blob_info.key(),save_as=object.name)

class OriginalServer(GenericServer):
    "Serve the original uploaded image. Currently unused."
    property = 'original'

class RemoteImage(webapp.RequestHandler):
    def get(self,key):
        test = db.get(key)
        if str(test.kind()).__eq__("RealmKeys"):
            realm = test
            if not realm:
                self.error(404)
            newupload = UploadRequestKeys()
            newupload.realm_key = realm
            newupload.put()
            result = dict(type='image',upload_url=str(self.request.url).replace(key,str(newupload.key())))
            json = simplejson.JSONEncoder().encode(result)
            self.response.headers['Content-Type'] = 'application/json'
            self.response.out.write(json)
        elif str(test.kind()).__eq__("UploadRequestKeys"):
            url = self.request.url
            context = {
                "url":url,
                "type":'image',
                       }
            path = os.path.join(os.path.dirname(__file__), 'templates','upload_form.html')
            # render the template with the provided context
            self.response.out.write(template.render(path, context))

    def post(self,key):
        checkkey = UploadRequestKeys.get(key)
        if not checkkey:
            self.error(404)
        checkkey.delete()
        img = self.request.get("img")
        # if we don't have image data we'll quit now
        if not img:
            return None
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
        #self.response.out.write(simplejson.dumps({'img_url'::}))
        context = {
                "image":True,
                "img_url":'http://org-images.appspot.com/i/img?id=%s'%image.key(),
                "thumb_url":'http://org-images.appspot.com/i/thumb?id=%s'%image.key()
                }
        path = os.path.join(os.path.dirname(__file__), 'templates','show_links.html')
        # render the template with the provided context
        self.response.out.write(template.render(path, context))
        

class RemoteBlob(blobstore_handlers.BlobstoreUploadHandler):
    def get(self,key):
        test = db.get(key)
        if str(test.kind()).__eq__("RealmKeys"):
            realm = test
            if not realm:
                self.error(404)
            newupload = UploadRequestKeys()
            newupload.realm_key = realm
            newupload.put()
            result = dict(type='blob',upload_url=str(self.request.url).replace(key,str(newupload.key())))
            json = simplejson.JSONEncoder().encode(result)
            self.response.headers['Content-Type'] = 'application/json'
            self.response.out.write(json)
        elif str(test.kind()).__eq__("UploadRequestKeys"):
            url = self.request.url
            context = {
                "type":'blob',
                "url":url,
                       }
            path = os.path.join(os.path.dirname(__file__), 'templates','upload_form.html')
            # render the template with the provided context
            self.response.out.write(template.render(path, context))

    def post(self):
        upload_files = self.get_uploads('file')  # 'file' is file upload field in the form
        blob_info = upload_files[0]
        blobfile = BlobFile()
        blobfile.blobkey = blob_info.key()
        blobfile.name = blob_info.filename
        blobfile.user = users.get_current_user()
        blobfile.put()
        context = {
                "image":False,
                'blob_url':'http://org-images.appspot.com/i/blob?id=%s'%blobfile.key,
                }
        path = os.path.join(os.path.dirname(__file__), 'templates','show_links.html')
        # render the template with the provided context
        self.response.out.write(template.render(path, context))

application = webapp.WSGIApplication([
    ('/i/blob', BlobServer),
    ('/i/css', CSSServer),
    ('/i/jscript', JScriptServer),
    ('/i/img', ImageServer),
    ('/i/thumb', ThumbServer),
    (r'/remote/upload/blob/(.*)', RemoteBlob),
    (r'/remote/upload/image/(.*)', RemoteImage),
], debug=True)

def main():
    "Run the application"
    run_wsgi_app(application)

if __name__ == '__main__':
    main()