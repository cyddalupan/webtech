from django.urls import path
from .views import save_facebook_chat, chat_test_page

urlpatterns = [
    path('webhook/', save_facebook_chat, name='save_facebook_chat'),
    path('test-chat/', chat_test_page, name='test_chat_page'),
]
