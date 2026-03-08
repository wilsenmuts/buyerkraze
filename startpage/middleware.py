from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from .models import ActiveSession, SiteSettings

class SessionTrackingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Skip for admin and static files
        if request.path.startswith('/admin') or request.path.startswith('/static'):
            return None
        
        # Get or create session key
        if not request.session.session_key:
            request.session.create()
        
        session_key = request.session.session_key
        user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
        ip_address = self.get_client_ip(request)
        page_url = request.path
        
        # Update or create active session
        ActiveSession.objects.update_or_create(
            session_key=session_key,
            defaults={
                'user_agent': user_agent,
                'ip_address': ip_address,
                'is_authenticated': request.user.is_authenticated,
                'username': request.user.username if request.user.is_authenticated else '',
                'page_url': page_url,
            }
        )
        
        # Clean up old sessions (inactive for more than 30 minutes)
        cutoff_time = timezone.now() - timedelta(minutes=30)
        ActiveSession.objects.filter(last_activity__lt=cutoff_time).delete()
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class SiteMaintenanceMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Skip for admin and superusers
        if request.path.startswith('/admin') or (request.user.is_authenticated and request.user.is_superuser):
            return None
        
        # Check if site is active
        site_settings = SiteSettings.load()
        if not site_settings.site_active:
            return render(request, 'maintenance.html', {
                'message': site_settings.maintenance_message
            }, status=503)
        
        return None
