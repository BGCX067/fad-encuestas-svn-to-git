from django.http import HttpResponse
from django.utils import simplejson

class JsonResponse(HttpResponse):
    """
    A little helper class to return JSON data.
    """
    def __init__(self, data):
        HttpResponse.__init__(
            self,
            content=simplejson.dumps(data),
            mimetype='application/json'
        )
