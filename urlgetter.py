from django.utils import simplejson
from google.appengine.api import urlfetch
from StringIO import StringIO

import logging

class geturl:
    def __init__(self,url):
        response = StringIO(urlfetch.fetch(url).content)
        self.result = simplejson.load(response)
        logging.getLogger().debug(self.result)

    def get_url(self):
        if self.result:
            return self.result['upload_url']
        return None