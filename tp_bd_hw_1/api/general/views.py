from json import dumps
from django.http import HttpResponse

def clear(request):
    result = {}
    return HttpResponse(dumps(result))

def status(request):
    result = {}
    return HttpResponse(dumps(result))


