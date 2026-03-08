from django.urls import path
from .views import start_view, article_list, event_list, article_detail, event_detail, redirect_to_country
from .api_views import ArticleListCreateAPIView, ArticleDetailAPIView, article_like, article_dislike
from .admin_views import admin_dashboard, get_active_sessions, toggle_site_status, update_maintenance_message, clear_inactive_sessions

urlpatterns = [
    path('', start_view, name='start'),
    path('articles/', article_list, name='article_list'),
    path('articles/<int:pk>/', article_detail, name='article_detail'),
    path('events/', event_list, name='event_list'),
    path('redirect/', redirect_to_country, name='redirect_to_country'),
    path('events/<int:pk>/', event_detail, name='event_detail'),
    
    # API endpoints
    path('api/articles/', ArticleListCreateAPIView.as_view(), name='api_article_list'),
    path('api/articles/<int:pk>/', ArticleDetailAPIView.as_view(), name='api_article_detail'),
    path('api/articles/<int:pk>/like/', article_like, name='api_article_like'),
    path('api/articles/<int:pk>/dislike/', article_dislike, name='api_article_dislike'),
    
    # Admin dashboard endpoints
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/sessions/', get_active_sessions, name='get_active_sessions'),
    path('admin-dashboard/toggle-site/', toggle_site_status, name='toggle_site_status'),
    path('admin-dashboard/update-maintenance/', update_maintenance_message, name='update_maintenance_message'),
    path('admin-dashboard/clear-sessions/', clear_inactive_sessions, name='clear_inactive_sessions'),
]