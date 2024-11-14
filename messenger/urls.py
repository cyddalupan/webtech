from django.urls import path
from .views import save_facebook_chat, chat_test_page, get_oldest_uncopied_user, mark_as_copied

urlpatterns = [
    path('webhook/', save_facebook_chat, name='save_facebook_chat'),
    path('test-chat/', chat_test_page, name='test_chat_page'),
    path('uncopied_user/', get_oldest_uncopied_user, name='get_oldest_uncopied_user'),
    path('mark-as-copied/<str:facebook_ids>/', mark_as_copied, name='mark_as_copied'),
]
