from json import dumps
from django.http import HttpResponse

def close_thread(request):
    result = {}
    return HttpResponse(dumps(result)) 

def create(request):
    result = {}
    return HttpResponse(dumps(result))

def details(request):
    result = {}
    return HttpResponse(dumps(result))

def list_threads(request):
    result = {}
    return HttpResponse(dumps(result))

def listPosts(request):
    result = {}
    return HttpResponse(dumps(result))

def open_thread(request):
    result = {}
    return HttpResponse(dumps(result))

def remove(request):
    result = {}
    return HttpResponse(dumps(result))

def restore(request):
    result = {}
    return HttpResponse(dumps(result))

def subscribe(request):
    result = {}
    return HttpResponse(dumps(result))

def unsubscribe(request):
    result = {}
    return HttpResponse(dumps(result))

def update(request):
    result = {}
    return HttpResponse(dumps(result))

def vote(request):
    result = {}
    return HttpResponse(dumps(result))
