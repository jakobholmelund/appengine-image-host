from django.utils import simplejson
from google.appengine.api import urlfetch
from StringIO import StringIO

import logging

class geturl:
    def __init__(self,url):
        self.result = dict(upload_url=None)
        try:
            response = StringIO(urlfetch.fetch(url).content)
            self.result = simplejson.load(response)
        except urlfetch.DownloadError:
            logging.getLogger().info(r"The request to filehost could not be established")
        except ValueError:
            logging.getLogger().info(r"JSON could not be decoded")
    def get_url(self):
        if self.result["upload_url"]:
            return self.result["upload_url"]
        return None