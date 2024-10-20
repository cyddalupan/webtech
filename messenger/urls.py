from django.urls import path
from .views import handle_facebook_chat

urlpatterns = [
    path('webhook/', handle_facebook_chat, name='handle_facebook_chat'),
]
