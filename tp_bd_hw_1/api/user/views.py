from json import dumps
from django.http import HttpResponse


def create(request):
    result = {}
    return HttpResponse(dumps(result))

def details(request):
    result = {}
    return HttpResponse(dumps(result))

def follow(request):
    result = {}
    return HttpResponse(dumps(result))

def listFollowers(request):
    result = {}
    return HttpResponse(dumps(result))

def listFollowing(request):
    result = {}
    return HttpResponse(dumps(result))

def listPosts(request):
    result = {}
    return HttpResponse(dumps(result))

def unfollow(request):
    result = {}
    return HttpResponse(dumps(result))

def updateProfile(request):
    result = {}
    return HttpResponse(dumps(result))

