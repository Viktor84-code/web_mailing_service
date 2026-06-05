from django.contrib import admin
from .models import Mailing

@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'is_sent', 'first_sent_at', 'end_at', 'message')
    list_filter = ('status', 'is_sent')
    search_fields = ('message__subject',)
