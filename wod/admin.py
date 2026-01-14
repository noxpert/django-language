from django.contrib import admin
from .models import WordOfDay


@admin.register(WordOfDay)
class WordOfDayAdmin(admin.ModelAdmin):
    list_display = ('word', 'language', 'definition', 'created_at')
    list_filter = ('language', 'created_at')
    search_fields = ('word', 'definition')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Word Information', {
            'fields': ('word', 'language', 'definition')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
