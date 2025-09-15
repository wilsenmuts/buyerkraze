from django.urls import path
from .views import start_view, article_list, event_list, article_detail, event_detail, redirect_to_country

urlpatterns = [
    path('', start_view, name='start'),
    path('articles/', article_list, name='article_list'),
    path('articles/<int:pk>/', article_detail, name='article_detail'),
    path('events/', event_list, name='event_list'),
    path('redirect/', redirect_to_country, name='redirect_to_country'),
    path('events/<int:pk>/', event_detail, name='event_detail'),
]