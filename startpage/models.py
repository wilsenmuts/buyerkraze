from django.db import models

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