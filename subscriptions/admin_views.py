from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
from .models import App, AccessKey, Subscription


def is_superuser(user):
    return user.is_authenticated and user.is_superuser


@user_passes_test(is_superuser, login_url='/admin/login/')
def subscription_list(request):
    """View all subscriptions with filtering."""
    subscriptions = Subscription.objects.select_related('access_key', 'app').all()

    # App filter
    app_filter = request.GET.get('app')
    if app_filter:
        subscriptions = subscriptions.filter(app__code=app_filter)

    # Status filter
    status_filter = request.GET.get('status')
    if status_filter:
        subscriptions = subscriptions.filter(status=status_filter)

    # Tier filter
    tier_filter = request.GET.get('tier')
    if tier_filter:
        subscriptions = subscriptions.filter(access_key_id=tier_filter)

    # Search
    search = request.GET.get('q')
    if search:
        subscriptions = subscriptions.filter(
            Q(user_name__icontains=search) |
            Q(user_email__icontains=search) |
            Q(generated_key__icontains=search)
        )

    apps = App.objects.filter(is_active=True)
    access_tiers = AccessKey.objects.select_related('app').all()

    # Global counts (unfiltered)
    total_all = Subscription.objects.count()
    active_count = Subscription.objects.filter(status='active').count()
    expired_count = Subscription.objects.filter(status='expired').count()
    cancelled_count = Subscription.objects.filter(status='cancelled').count()
    pending_count = Subscription.objects.filter(status='pending').count()

    context = {
        'subscriptions': subscriptions,
        'apps': apps,
        'access_tiers': access_tiers,
        'current_app': app_filter,
        'current_status': status_filter,
        'current_tier': tier_filter,
        'current_search': search,
        'status_choices': Subscription.STATUS_CHOICES,
        'total_all': total_all,
        'active_count': active_count,
        'expired_count': expired_count,
        'cancelled_count': cancelled_count,
        'pending_count': pending_count,
    }
    return render(request, 'subscriptions/subscription_list.html', context)


@user_passes_test(is_superuser, login_url='/admin/login/')
def subscription_analytics(request):
    """Subscription analytics dashboard."""
    now = timezone.now()
    thirty_days_ago = now - timedelta(days=30)
    seven_days_ago = now - timedelta(days=7)

    # Core stats
    total_subscriptions = Subscription.objects.count()
    active_subscriptions = Subscription.objects.filter(status='active').count()
    expired_subscriptions = Subscription.objects.filter(status='expired').count()
    cancelled_subscriptions = Subscription.objects.filter(status='cancelled').count()
    pending_subscriptions = Subscription.objects.filter(status='pending').count()

    # Subscriptions by tier
    subscriptions_by_tier = (
        Subscription.objects.values('access_key__name', 'access_key__price')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    # Active subscriptions by tier
    active_by_tier = (
        Subscription.objects.filter(status='active')
        .values('access_key__name')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    # New subscriptions (last 30 days)
    new_subscriptions_30d = Subscription.objects.filter(created_at__gte=thirty_days_ago).count()
    new_subscriptions_7d = Subscription.objects.filter(created_at__gte=seven_days_ago).count()

    # Expiring soon (within 7 days)
    expiring_soon = Subscription.objects.filter(
        status='active',
        end_date__gte=now,
        end_date__lte=now + timedelta(days=7)
    ).count()

    # Already expired but still marked active (auto-expire candidates)
    overdue = Subscription.objects.filter(
        status='active',
        end_date__lt=now
    ).count()

    # Subscriptions created over last 30 days (for chart)
    daily_new = []
    for i in range(30, -1, -1):
        day = now - timedelta(days=i)
        next_day = day + timedelta(days=1)
        count = Subscription.objects.filter(
            created_at__gte=day,
            created_at__lt=next_day
        ).count()
        daily_new.append({
            'date': day.strftime('%Y-%m-%d'),
            'count': count,
        })

    # Subscriptions by app
    subscriptions_by_app = (
        Subscription.objects.values('app__name', 'app__code')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    # Revenue stats (approximate based on active subscriptions)
    total_potential_revenue = sum(
        (s.access_key.price for s in
         Subscription.objects.filter(status='active').select_related('access_key')),
        0
    )

    apps = App.objects.filter(is_active=True)
    access_tiers = AccessKey.objects.select_related('app').all()

    context = {
        'total_subscriptions': total_subscriptions,
        'active_subscriptions': active_subscriptions,
        'expired_subscriptions': expired_subscriptions,
        'cancelled_subscriptions': cancelled_subscriptions,
        'pending_subscriptions': pending_subscriptions,
        'subscriptions_by_tier': subscriptions_by_tier,
        'active_by_tier': active_by_tier,
        'subscriptions_by_app': subscriptions_by_app,
        'new_subscriptions_30d': new_subscriptions_30d,
        'new_subscriptions_7d': new_subscriptions_7d,
        'expiring_soon': expiring_soon,
        'overdue': overdue,
        'daily_new': daily_new,
        'total_potential_revenue': total_potential_revenue,
        'apps': apps,
        'access_tiers': access_tiers,
        'now': now,
    }
    return render(request, 'subscriptions/subscription_analytics.html', context)


# ─── Manage Apps ──────────────────────────────────────────────────

@user_passes_test(is_superuser, login_url='/admin/login/')
def manage_apps(request):
    """List, create, edit, and delete applications."""
    apps = App.objects.all().order_by('name')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'create':
            name = request.POST.get('name', '').strip()
            code = request.POST.get('code', '').strip()
            description = request.POST.get('description', '').strip()

            if name and code:
                if App.objects.filter(code=code).exists():
                    messages.error(request, f'App with code "{code}" already exists.')
                elif App.objects.filter(name=name).exists():
                    messages.error(request, f'App with name "{name}" already exists.')
                else:
                    App.objects.create(name=name, code=code, description=description)
                    messages.success(request, f'App "{name}" created successfully.')
            else:
                messages.error(request, 'Name and code are required.')

        elif action == 'edit':
            app_id = request.POST.get('app_id')
            name = request.POST.get('name', '').strip()
            code = request.POST.get('code', '').strip()
            description = request.POST.get('description', '').strip()
            is_active = request.POST.get('is_active') == 'on'

            app = get_object_or_404(App, pk=app_id)
            if name and code:
                if App.objects.filter(code=code).exclude(pk=app_id).exists():
                    messages.error(request, f'Another app already uses code "{code}".')
                elif App.objects.filter(name=name).exclude(pk=app_id).exists():
                    messages.error(request, f'Another app already uses name "{name}".')
                else:
                    app.name = name
                    app.code = code
                    app.description = description
                    app.is_active = is_active
                    app.save()
                    messages.success(request, f'App "{name}" updated successfully.')
            else:
                messages.error(request, 'Name and code are required.')

        elif action == 'delete':
            app_id = request.POST.get('app_id')
            app = get_object_or_404(App, pk=app_id)
            # Check if app has tiers or subscriptions
            if AccessKey.objects.filter(app=app).exists():
                messages.error(request, f'Cannot delete "{app.name}" — it has tiers assigned. Remove tiers first.')
            else:
                name = app.name
                app.delete()
                messages.success(request, f'App "{name}" deleted successfully.')

        return redirect('manage_apps')

    return render(request, 'subscriptions/manage_apps.html', {'apps': apps})


# ─── Manage Tiers ─────────────────────────────────────────────────

@user_passes_test(is_superuser, login_url='/admin/login/')
def manage_tiers(request):
    """List, create, edit, and delete access key tiers."""
    app_filter = request.GET.get('app')
    tiers = AccessKey.objects.select_related('app').all().order_by('app__name', 'price')
    if app_filter:
        tiers = tiers.filter(app__code=app_filter)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'create':
            app_id = request.POST.get('app_id')
            name = request.POST.get('name', '').strip()
            key_prefix = request.POST.get('key_prefix', '').strip()
            description = request.POST.get('description', '').strip()
            price = request.POST.get('price', '0.00')
            duration_days = request.POST.get('duration_days', 30)
            max_requests_per_day = request.POST.get('max_requests_per_day', 100)
            max_concurrent_sessions = request.POST.get('max_concurrent_sessions', 1)

            app = get_object_or_404(App, pk=app_id)
            if name and key_prefix:
                if AccessKey.objects.filter(app=app, name=name).exists():
                    messages.error(request, f'Tier "{name}" already exists for "{app.name}".')
                else:
                    AccessKey.objects.create(
                        app=app, name=name, key_prefix=key_prefix,
                        description=description, price=price,
                        duration_days=duration_days,
                        max_requests_per_day=max_requests_per_day,
                        max_concurrent_sessions=max_concurrent_sessions,
                    )
                    messages.success(request, f'Tier "{name}" created for "{app.name}".')
            else:
                messages.error(request, 'Tier name and key prefix are required.')

        elif action == 'edit':
            tier_id = request.POST.get('tier_id')
            name = request.POST.get('name', '').strip()
            key_prefix = request.POST.get('key_prefix', '').strip()
            description = request.POST.get('description', '').strip()
            price = request.POST.get('price', '0.00')
            duration_days = request.POST.get('duration_days', 30)
            max_requests_per_day = request.POST.get('max_requests_per_day', 100)
            max_concurrent_sessions = request.POST.get('max_concurrent_sessions', 1)
            is_active = request.POST.get('is_active') == 'on'

            tier = get_object_or_404(AccessKey, pk=tier_id)
            if name and key_prefix:
                if AccessKey.objects.filter(app=tier.app, name=name).exclude(pk=tier_id).exists():
                    messages.error(request, f'Another tier named "{name}" already exists for "{tier.app.name}".')
                else:
                    tier.name = name
                    tier.key_prefix = key_prefix
                    tier.description = description
                    tier.price = price
                    tier.duration_days = duration_days
                    tier.max_requests_per_day = max_requests_per_day
                    tier.max_concurrent_sessions = max_concurrent_sessions
                    tier.is_active = is_active
                    tier.save()
                    messages.success(request, f'Tier "{name}" updated successfully.')
            else:
                messages.error(request, 'Tier name and key prefix are required.')

        elif action == 'delete':
            tier_id = request.POST.get('tier_id')
            tier = get_object_or_404(AccessKey, pk=tier_id)
            if Subscription.objects.filter(access_key=tier).exists():
                messages.error(
                    request,
                    f'Cannot delete tier "{tier.name}" — it has active subscriptions. '
                    f'Deactivate it instead.'
                )
            else:
                name = tier.name
                tier.delete()
                messages.success(request, f'Tier "{name}" deleted successfully.')

        return redirect('manage_tiers')

    apps = App.objects.all()
    current_app = app_filter
    # Get tier counts per app for stats
    app_tier_counts = {a.code: AccessKey.objects.filter(app=a).count() for a in apps}

    context = {
        'tiers': tiers,
        'apps': apps,
        'current_app': current_app,
        'app_tier_counts': app_tier_counts,
    }
    return render(request, 'subscriptions/manage_tiers.html', context)
