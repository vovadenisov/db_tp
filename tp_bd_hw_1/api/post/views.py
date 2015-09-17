from json import dumps
from django.http import HttpResponse

def create(request):
    result = {}
    return HttpResponse(dumps(result))

def details(request):
    result = {}
    return HttpResponse(dumps(result))

def list_posts(request):
    result = {}
    return HttpResponse(dumps(result))

def remove(request):
    result = {}
    return HttpResponse(dumps(result))

def restore(request):
    result = {}
    return HttpResponse(dumps(result))

def update(request):
    result = {}
    return HttpResponse(dumps(result))

def vote(request):
    result = {}
    return HttpResponse(dumps(result))
