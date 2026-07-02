from django.db import models
from django.utils import timezone
import secrets


class App(models.Model):
    """Represents an application that uses the subscription system."""
    name = models.CharField(max_length=100, unique=True, help_text="Application name (e.g., Campus Eats, Reconna)")
    code = models.CharField(max_length=50, unique=True, help_text="Unique API code to identify the app (e.g., campuseats, reconna)")
    description = models.TextField(blank=True, help_text="Description of the application")
    is_active = models.BooleanField(default=True, help_text="Whether this app is active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.code})"

    class Meta:
        verbose_name = 'Application'
        verbose_name_plural = 'Applications'
        db_table = 'apps'
        ordering = ['name']


class AccessKey(models.Model):
    """Defines a tier/plan of access with specific permissions and limits."""
    app = models.ForeignKey(App, on_delete=models.CASCADE, related_name='access_keys', null=True, blank=True, help_text="The application this tier belongs to")
    name = models.CharField(max_length=100, help_text="Name of the access tier (e.g., Basic, Premium, Enterprise)")
    key_prefix = models.CharField(max_length=20, help_text="Prefix for generated subscription keys (e.g., basic_, prem_, ent_)")
    description = models.TextField(blank=True, help_text="Description of what this tier offers")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    duration_days = models.PositiveIntegerField(default=30, help_text="Number of days a subscription to this tier is valid")
    max_requests_per_day = models.PositiveIntegerField(default=100, help_text="Maximum API requests allowed per day")
    max_concurrent_sessions = models.PositiveIntegerField(default=1, help_text="Maximum concurrent sessions allowed")
    is_active = models.BooleanField(default=True, help_text="Whether this tier is currently available for purchase")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.app.name} - {self.name}"

    class Meta:
        verbose_name = 'Access Key Tier'
        verbose_name_plural = 'Access Key Tiers'
        db_table = 'access_keys'
        ordering = ['app__name', 'price']
        constraints = []


class Subscription(models.Model):
    """Maps a subscriber to an AccessKey tier with a generated API key and status tracking."""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
        ('pending', 'Pending'),
    ]

    app = models.ForeignKey(App, on_delete=models.CASCADE, related_name='subscriptions', null=True, blank=True, help_text="The application this subscription belongs to")
    access_key = models.ForeignKey(AccessKey, on_delete=models.CASCADE, related_name='subscriptions', help_text="The access tier this subscription belongs to")
    user_email = models.EmailField(help_text="Email of the subscriber")
    user_name = models.CharField(max_length=100, help_text="Name of the subscriber")
    generated_key = models.CharField(max_length=64, unique=True, editable=False, help_text="The generated API key for this subscription")
    start_date = models.DateTimeField(default=timezone.now, help_text="When the subscription starts")
    end_date = models.DateTimeField(help_text="When the subscription expires")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', db_index=True)
    notes = models.TextField(blank=True, help_text="Additional notes about this subscription")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.generated_key:
            self.generated_key = self._generate_key()
        if not self.end_date and self.access_key:
            self.end_date = self.start_date + timezone.timedelta(days=self.access_key.duration_days)
        # Auto-set app from access_key if not explicitly provided
        if not self.app_id and self.access_key:
            self.app = self.access_key.app
        super().save(*args, **kwargs)

    def _generate_key(self):
        """Generate a unique API key with the tier's prefix."""
        prefix = self.access_key.key_prefix if self.access_key else ''
        random_part = secrets.token_urlsafe(48)
        return f"{prefix}{random_part}"

    def is_expired(self):
        return timezone.now() > self.end_date

    def days_remaining(self):
        if self.is_expired():
            return 0
        return (self.end_date - timezone.now()).days

    def __str__(self):
        return f"{self.user_name} - {self.access_key.name} ({self.status})"

    class Meta:
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'
        db_table = 'subscriptions'
        ordering = ['-created_at']
