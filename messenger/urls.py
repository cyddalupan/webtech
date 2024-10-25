from django.urls import path
from .views import save_facebook_chat, chat_test_page, get_user_by_facebook_id

urlpatterns = [
    path('webhook/', save_facebook_chat, name='save_facebook_chat'),
    path('test-chat/', chat_test_page, name='test_chat_page'),
    path('user/<str:facebook_id>/', get_user_by_facebook_id, name='get_user_by_facebook_id'),
]
