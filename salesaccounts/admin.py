from django.contrib import admin
from .models import SalesAccount, Deal, ContactActivity


@admin.register(SalesAccount)
class SalesAccountAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'contact_person', 'email', 'status', 
        'account_value', 'deals_count', 'last_contact_date', 'created_by'
    ]
    list_filter = ['status', 'created_at', 'assigned_to']
    search_fields = ['name', 'contact_person', 'email']
    readonly_fields = ['created_at', 'updated_at', 'deals_count', 'last_contact_date']
    
    fieldsets = (
        ('Company Information', {
            'fields': ('name', 'contact_person', 'email', 'phone', 'location')
        }),
        ('Account Details', {
            'fields': ('account_value', 'status', 'deals_count', 'last_contact_date')
        }),
        ('Assignment', {
            'fields': ('created_by', 'assigned_to')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Deal)
class DealAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'account', 'value', 'stage', 'probability', 
        'expected_close_date', 'created_by'
    ]
    list_filter = ['stage', 'created_at', 'account']
    search_fields = ['title', 'account__name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Deal Information', {
            'fields': ('account', 'title', 'value', 'stage', 'probability')
        }),
        ('Timeline', {
            'fields': ('expected_close_date', 'created_at', 'updated_at')
        }),
        ('User', {
            'fields': ('created_by',)
        }),
    )


@admin.register(ContactActivity)
class ContactActivityAdmin(admin.ModelAdmin):
    list_display = [
        'account', 'activity_type', 'subject', 'performed_by', 'activity_date'
    ]
    list_filter = ['activity_type', 'activity_date', 'account']
    search_fields = ['subject', 'account__name', 'performed_by__username']
    readonly_fields = ['activity_date']
    
    fieldsets = (
        ('Activity Information', {
            'fields': ('account', 'activity_type', 'subject', 'description')
        }),
        ('Association', {
            'fields': ('deal', 'performed_by')
        }),
        ('Timing', {
            'fields': ('activity_date',)
        }),
    )
