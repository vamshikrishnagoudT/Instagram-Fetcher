from django.urls import path
from . import views

urlpatterns = [
    path('latest-post/', views.get_latest_post, name='latest_post'),
    path('post-tweet/', views.post_tweet, name='post_tweet'),
]