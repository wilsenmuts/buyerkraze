from django.contrib import admin
from .models import App, AccessKey, Subscription


@admin.register(App)
class AppAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'code')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(AccessKey)
class AccessKeyAdmin(admin.ModelAdmin):
    list_display = ('name', 'app', 'key_prefix', 'price', 'duration_days', 'max_requests_per_day', 'is_active', 'created_at')
    list_filter = ('is_active', 'app')
    search_fields = ('name', 'key_prefix')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user_name', 'user_email', 'app', 'access_key', 'generated_key_short', 'status', 'start_date', 'end_date', 'created_at')
    list_filter = ('status', 'app', 'access_key', 'created_at')
    search_fields = ('user_name', 'user_email', 'generated_key')
    readonly_fields = ('generated_key', 'created_at', 'updated_at')

    def generated_key_short(self, obj):
        return f"{obj.generated_key[:16]}..."
    generated_key_short.short_description = 'API Key'
