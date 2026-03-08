from django.contrib import admin
from .models import CountryLink, Article, Event, EventSubscription, APIKey, ArticleInteraction, SiteSettings, ActiveSession

@admin.register(CountryLink)
class CountryLinkAdmin(admin.ModelAdmin):
    list_display = ('country_name', 'url', 'hit_count')

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'published_date', 'updated_date', 'view_count', 'likes', 'dislikes')
    readonly_fields = ('view_count', 'likes', 'dislikes')

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_date', 'location', 'country_region', 'is_subscribable')

@admin.register(EventSubscription)
class EventSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user_name', 'user_email', 'user_phone', 'event', 'submitted_date')
    list_filter = ('event',)

@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ('name', 'key', 'created_date', 'is_active')
    list_filter = ('is_active',)
    readonly_fields = ('key', 'created_date')

@admin.register(ArticleInteraction)
class ArticleInteractionAdmin(admin.ModelAdmin):
    list_display = ('article', 'interaction_type', 'session_id', 'created_date')
    list_filter = ('interaction_type', 'created_date')

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('site_active', 'updated_at', 'updated_by')
    readonly_fields = ('updated_at',)
    
    def has_add_permission(self, request):
        # Prevent adding more than one instance
        return not SiteSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Prevent deletion
        return False

@admin.register(ActiveSession)
class ActiveSessionAdmin(admin.ModelAdmin):
    list_display = ('username', 'ip_address', 'page_url', 'last_activity', 'is_authenticated')
    list_filter = ('is_authenticated', 'last_activity')
    search_fields = ('username', 'ip_address', 'page_url')
    readonly_fields = ('session_key', 'user_agent', 'ip_address', 'last_activity', 'is_authenticated', 'username', 'page_url')
    
    def has_add_permission(self, request):
        return False