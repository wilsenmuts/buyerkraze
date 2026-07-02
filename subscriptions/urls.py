from django.urls import path
from .api_views import (
    AppListAPIView,
    AccessKeyListCreateAPIView,
    AccessKeyDetailAPIView,
    TiersByAppCodeAPIView,
    SubscriptionListCreateAPIView,
    SubscriptionDetailAPIView,
    cancel_subscription,
    validate_key,
)
from .admin_views import subscription_list, subscription_analytics, manage_apps, manage_tiers

urlpatterns = [
    # Admin management views
    path('admin/apps/', manage_apps, name='manage_apps'),
    path('admin/tiers/', manage_tiers, name='manage_tiers'),

    # Admin dashboard views
    path('admin/subscriptions/', subscription_list, name='subscription_list'),
    path('admin/subscriptions/analytics/', subscription_analytics, name='subscription_analytics'),

    # App endpoints
    path('api/apps/', AppListAPIView.as_view(), name='api_app_list'),

    # Access Key Tier endpoints
    path('api/access-keys/', AccessKeyListCreateAPIView.as_view(), name='api_access_key_list'),
    path('api/access-keys/<int:pk>/', AccessKeyDetailAPIView.as_view(), name='api_access_key_detail'),

    # Tiers by app code (for displaying tiers on a specific app)
    path('api/tiers/<slug:app_code>/', TiersByAppCodeAPIView.as_view(), name='api_tiers_by_app'),

    # Subscription endpoints
    path('api/subscriptions/', SubscriptionListCreateAPIView.as_view(), name='api_subscription_list'),
    path('api/subscriptions/<int:pk>/', SubscriptionDetailAPIView.as_view(), name='api_subscription_detail'),
    path('api/subscriptions/<int:pk>/cancel/', cancel_subscription, name='api_subscription_cancel'),

    # Validation endpoint
    path('api/validate-key/', validate_key, name='api_validate_key'),
]
