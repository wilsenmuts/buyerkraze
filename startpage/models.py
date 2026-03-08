from django.db import models
import secrets

class CountryLink(models.Model):
    country_name = models.CharField(max_length=100, unique=True)
    url = models.URLField()
    hit_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.country_name

    class Meta:
        verbose_name_plural = 'Country Links'
        ordering = ['country_name']
        db_table = 'country_links'


class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    published_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    featured_image = models.ImageField(upload_to='articles/featured/', blank=True, null=True)
    top_image = models.ImageField(upload_to='articles/top/', blank=True, null=True)
    view_count = models.PositiveIntegerField(default=0)
    likes = models.PositiveIntegerField(default=0)
    dislikes = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-published_date']
        db_table = 'articles'

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    event_date = models.DateTimeField()
    location = models.CharField(max_length=200, blank=True)
    country_region = models.CharField(max_length=100, default='World', help_text='Country, region, or World')
    featured_image = models.ImageField(upload_to='events/featured/', blank=True, null=True)
    is_subscribable = models.BooleanField(default=False)
    contact_email = models.EmailField(blank=True)
    contact_number = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-event_date']
        db_table = 'events'

class EventSubscription(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='subscriptions')
    user_name = models.CharField(max_length=100)
    user_email = models.EmailField()
    user_phone = models.CharField(max_length=50, blank=True)
    additional_details = models.TextField(blank=True)
    submitted_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_name} - {self.event.title}"

    class Meta:
        db_table = 'event_subscriptions'

class APIKey(models.Model):
    key = models.CharField(max_length=64, unique=True, editable=False)
    name = models.CharField(max_length=100, help_text="Name to identify this API key")
    created_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def save(self, *args, **kwargs):
        if not self.key:
            self.key = secrets.token_urlsafe(48)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} - {self.key[:8]}..."
    
    class Meta:
        db_table = 'api_keys'
        verbose_name = 'API Key'
        verbose_name_plural = 'API Keys'

class ArticleInteraction(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='interactions')
    session_id = models.CharField(max_length=100, help_text="Session or IP to prevent duplicate votes")
    interaction_type = models.CharField(max_length=10, choices=[('like', 'Like'), ('dislike', 'Dislike')])
    created_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'article_interactions'
        unique_together = ['article', 'session_id']

class SiteSettings(models.Model):
    """Singleton model to store site-wide settings"""
    site_active = models.BooleanField(default=True, help_text="Toggle to activate/deactivate the entire site")
    maintenance_message = models.TextField(default="Site is currently under maintenance. Please check back later.", help_text="Message to show when site is deactivated")
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.CharField(max_length=100, blank=True)
    
    class Meta:
        verbose_name = 'Site Settings'
        verbose_name_plural = 'Site Settings'
        db_table = 'site_settings'
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        self.pk = 1
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        # Prevent deletion - return a tuple to match base signature
        return (0, {})
    
    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
    
    def __str__(self):
        return f"Site Settings - Active: {self.site_active}"

class ActiveSession(models.Model):
    """Track active user sessions"""
    session_key = models.CharField(max_length=40, unique=True)
    user_agent = models.TextField()
    ip_address = models.GenericIPAddressField()
    last_activity = models.DateTimeField(auto_now=True)
    is_authenticated = models.BooleanField(default=False)
    username = models.CharField(max_length=150, blank=True)
    page_url = models.CharField(max_length=500, blank=True)
    
    class Meta:
        db_table = 'active_sessions'
        ordering = ['-last_activity']
    
    def __str__(self):
        return f"{self.username or 'Anonymous'} - {self.ip_address}"