from django.urls import path
from .views import save_facebook_chat

urlpatterns = [
    path('webhook/', save_facebook_chat, name='save_facebook_chat'),
]
