from django.contrib import admin
from .models import FacebookPage

@admin.register(FacebookPage)
class FacebookPageAdmin(admin.ModelAdmin):
    list_display = ('page_id', 'name', 'details')
    search_fields = ('name', 'page_id')
    list_filter = ('name',)