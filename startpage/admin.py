from django.contrib import admin
from .models import CountryLink, Article, Event, EventSubscription

@admin.register(CountryLink)
class CountryLinkAdmin(admin.ModelAdmin):
    list_display = ('country_name', 'url', 'hit_count')

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'published_date', 'updated_date')

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_date', 'location', 'country_region', 'is_subscribable')

@admin.register(EventSubscription)
class EventSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user_name', 'user_email', 'user_phone', 'event', 'submitted_date')
    list_filter = ('event',)