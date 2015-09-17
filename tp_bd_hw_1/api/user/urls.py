from django.conf.urls import include, url
from views import create, details, follow, listFollowers, listFollowing, listPosts, unfollow, updateProfile

urlpatterns = [
    url(r'^create/', create),
    url(r'^details/', details),
    url(r'^listFollowers/', listPosts),
    url(r'^listFollowing/', listPosts),
    url(r'^listPosts/', listPosts),
    url(r'^unfollow/', unfollow),
    url(r'^updateProfile/', updateProfile),
]
