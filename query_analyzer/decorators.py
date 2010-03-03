from django.http import HttpResponse
from django.utils import simplejson
from functools import wraps


def json_view(func):
    @wraps
    def wrapper(*args, **kwargs):
        content = func(*args, **kwargs)
        response = HttpResponse(content_type="application/json")
        simplejson.dump(content, response)
        return response
    return wrapper
