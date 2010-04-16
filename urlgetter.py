from django.utils import simplejson
from google.appengine.api import urlfetch
from StringIO import StringIO

import logging

class geturl:
    def __init__(self,url):
        try:
            response = StringIO(urlfetch.fetch(url).content)
            self.result = simplejson.load(response)
        except DownloadError:
            logging.getLogger().info(r"The request to filehost could not be established")

        
    def get_url(self):
        if self.result:
            return self.result['upload_url']
        return None