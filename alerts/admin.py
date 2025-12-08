from django.contrib import admin
from .models import Alert


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'description', 'created_at')
    list_filter = ('type', 'created_at')
    search_fields = ('description',)
