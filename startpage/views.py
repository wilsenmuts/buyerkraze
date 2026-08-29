from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import F
from django.utils import timezone
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CountryLink, Article, Event
from .forms import SubscriptionForm, UserRegisterForm, ArticleForm
import geoip2.database
import os
import random
from django.conf import settings

def start_view(request):
    countries = CountryLink.objects.all()
    selected_country = request.session.get('selected_country')

    # Get random video from landing_page_videos folder
    video_folder = os.path.join(settings.BASE_DIR, 'startpage', 'static', 'landing_page_videos')
    try:
        videos = [f for f in os.listdir(video_folder) if f.endswith(('.mp4', '.webm', '.ogg'))]
        random_video = random.choice(videos) if videos else None
    except FileNotFoundError:
        random_video = None

    auto_detect = request.GET.get('auto', 'false') == 'true'
    if not selected_country and auto_detect:
        try:
            reader = geoip2.database.Reader(os.path.join(settings.GEOIP_PATH, 'GeoLite2-Country.mmdb'))
            ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
            response = reader.country(ip)
            country_name = response.country.name
            reader.close()
            if country_name:
                try:
                    country = CountryLink.objects.get(country_name__iexact=country_name)
                    country.hit_count = F('hit_count') + 1
                    country.save()
                    request.session['selected_country'] = country.country_name
                    return redirect(country.url)
                except CountryLink.DoesNotExist:
                    pass
        except (geoip2.errors.AddressNotFoundError, FileNotFoundError, ValueError):
            pass

    if request.method == 'POST':
        new_selection = request.POST.get('country')
        if new_selection:
            try:
                country = CountryLink.objects.get(country_name=new_selection)
                country.hit_count = F('hit_count') + 1
                country.save()
                request.session['selected_country'] = new_selection
                return redirect(country.url)
            except CountryLink.DoesNotExist:
                pass

    context = {
        'countries': countries,
        'selected_country': selected_country,
        'random_video': random_video,
    }
    return render(request, 'start.html', context)

def article_list(request):
    articles = Article.objects.all().order_by('-published_date')
    return render(request, 'article_list.html', {'articles': articles})

def article_detail(request, pk):
    article = get_object_or_404(Article, pk=pk)
    # Increment view count
    Article.objects.filter(pk=pk).update(view_count=F('view_count') + 1)
    article.refresh_from_db()
    return render(request, 'article_detail.html', {'article': article})

# ─── User Authentication ─────────────────────────────────────────

def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Account created successfully! Welcome, {user.username}.')
            return redirect('article_list')
    else:
        form = UserRegisterForm()
    return render(request, 'registration/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'article_list')
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'registration/login.html')

def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('article_list')

# ─── Article Creation (Modern Editor) ────────────────────────────

@login_required
def create_article(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            # If editor_mode is modern, store content as-is (preserves HTML)
            article.save()
            messages.success(request, 'Article created successfully!')
            return redirect('article_detail', pk=article.pk)
    else:
        form = ArticleForm(initial={'editor_mode': 'modern'})
    return render(request, 'create_article.html', {'form': form})

@login_required
def edit_article(request, pk):
    article = get_object_or_404(Article, pk=pk)
    # Only author or superuser can edit
    if request.user != article.author and not request.user.is_superuser:
        messages.error(request, 'You do not have permission to edit this article.')
        return redirect('article_detail', pk=pk)
    
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            form.save()
            messages.success(request, 'Article updated successfully!')
            return redirect('article_detail', pk=article.pk)
    else:
        form = ArticleForm(instance=article)
    return render(request, 'create_article.html', {'form': form, 'editing': True, 'article': article})

def event_list(request):
    # Only show events that haven't passed yet
    now = timezone.now()
    events = Event.objects.filter(event_date__gte=now).order_by('event_date')
    return render(request, 'event_list.html', {'events': events})

def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    
    # Check if event has already passed
    now = timezone.now()
    event_has_passed = event.event_date < now
    
    if request.method == 'POST' and event.is_subscribable and not event_has_passed:
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            subscription = form.save(commit=False)
            subscription.event = event
            subscription.save()
            return redirect('event_detail', pk=pk)
    else:
        form = SubscriptionForm() if (event.is_subscribable and not event_has_passed) else None
    
    return render(request, 'event_detail.html', {
        'event': event, 
        'form': form,
        'event_has_passed': event_has_passed
    })

def redirect_to_country(request):
    try:
        country = CountryLink.objects.get(country_name=request.session['selected_country'])
        return redirect(country.url)
    except CountryLink.DoesNotExist:
        return redirect('start')