from django.contrib import admin
from .models import Event, EventGuest
from apps.core.admin import BaseAccountAdmin

@admin.register(Event)
class EventAdmin(BaseAccountAdmin):
    list_display = ('name', 'creator', 'start_date', 'end_date', 'number', 'status')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'creator__email', 'nameprefix')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)

@admin.register(EventGuest) 
class EventGuestAdmin(BaseAccountAdmin):
    list_display = ('username', 'event', 'status', 'start_date', 'end_date')
    list_filter = ('status', 'event', 'created_at')
    search_fields = ('username','event')
    readonly_fields = ('created_at', 'updated_at', 'password')
    ordering = ('-created_at',)