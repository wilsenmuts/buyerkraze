from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .models import ActiveSession, SiteSettings
from django.contrib.auth import get_user_model
from subscriptions.models import Subscription
import platform

User = get_user_model()

def is_superuser(user):
    return user.is_authenticated and user.is_superuser

@user_passes_test(is_superuser, login_url='/admin/login/')
def admin_dashboard(request):
    """Main admin dashboard view"""
    site_settings = SiteSettings.load()
    
    # Get statistics
    total_sessions = ActiveSession.objects.count()
    authenticated_sessions = ActiveSession.objects.filter(is_authenticated=True).count()
    anonymous_sessions = total_sessions - authenticated_sessions
    
    # Get all users
    users = User.objects.all().order_by('-date_joined')
    
    # Subscription counts
    total_subscriptions = Subscription.objects.count()
    active_count = Subscription.objects.filter(status='active').count()
    expired_count = Subscription.objects.filter(status='expired').count()
    cancelled_count = Subscription.objects.filter(status='cancelled').count()

    context = {
        'site_settings': site_settings,
        'total_sessions': total_sessions,
        'authenticated_sessions': authenticated_sessions,
        'anonymous_sessions': anonymous_sessions,
        'users': users,
        'server_info': {
            'os': platform.system(),
            'os_version': platform.release(),
            'python_version': platform.python_version(),
        },
        'total_subscriptions': total_subscriptions,
        'active_count': active_count,
        'expired_count': expired_count,
        'cancelled_count': cancelled_count,
    }
    
    return render(request, 'admin_dashboard.html', context)

@user_passes_test(is_superuser, login_url='/admin/login/')
@require_http_methods(["GET"])
def get_active_sessions(request):
    """API endpoint to get active sessions (for AJAX polling)"""
    sessions = ActiveSession.objects.all()[:50]  # Limit to 50 most recent
    
    sessions_data = []
    for session in sessions:
        sessions_data.append({
            'id': session.id,
            'username': session.username or 'Anonymous',
            'ip_address': session.ip_address,
            'user_agent': session.user_agent[:100],  # Truncate for display
            'page_url': session.page_url,
            'last_activity': session.last_activity.isoformat(),
            'is_authenticated': session.is_authenticated,
        })
    
    return JsonResponse({
        'sessions': sessions_data,
        'total_count': ActiveSession.objects.count(),
        'timestamp': timezone.now().isoformat()
    })

@user_passes_test(is_superuser, login_url='/admin/login/')
@require_http_methods(["POST"])
def toggle_site_status(request):
    """Toggle site active/inactive status"""
    site_settings = SiteSettings.load()
    site_settings.site_active = not site_settings.site_active
    site_settings.updated_by = request.user.username
    site_settings.save()
    
    status = "activated" if site_settings.site_active else "deactivated"
    messages.success(request, f'Site has been {status} successfully!')
    
    return JsonResponse({
        'success': True,
        'site_active': site_settings.site_active,
        'message': f'Site has been {status}'
    })

@user_passes_test(is_superuser, login_url='/admin/login/')
@require_http_methods(["POST"])
def update_maintenance_message(request):
    """Update the maintenance message"""
    message = request.POST.get('message', '')
    
    if message:
        site_settings = SiteSettings.load()
        site_settings.maintenance_message = message
        site_settings.updated_by = request.user.username
        site_settings.save()
        
        messages.success(request, 'Maintenance message updated successfully!')
        return JsonResponse({
            'success': True,
            'message': 'Maintenance message updated'
        })
    
    return JsonResponse({
        'success': False,
        'message': 'Message cannot be empty'
    }, status=400)

@user_passes_test(is_superuser, login_url='/admin/login/')
def clear_inactive_sessions(request):
    """Clear all inactive sessions"""
    cutoff_time = timezone.now() - timedelta(minutes=30)
    deleted_count = ActiveSession.objects.filter(last_activity__lt=cutoff_time).delete()[0]
    
    messages.success(request, f'Cleared {deleted_count} inactive sessions!')
    return redirect('admin_dashboard')
