from django.contrib import admin
from .models import UserProfile, Chat

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('facebook_id', 'page_id',  'full_name', 'age', 'location')  # Customize what you want to see
    search_fields = ('facebook_id', 'page_id',  'full_name')  # Add search capability by these fields

@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'reply', 'timestamp')  # Customize what is shown in the admin list view
    list_filter = ('timestamp',)  # Filter chats by date
    search_fields = ('user__full_name', 'message', 'reply')  # Add search capabilities on user, message, and reply
