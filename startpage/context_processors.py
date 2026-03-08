from django.conf import settings

def social_media_links(request):
    """Make social media links available to all templates"""
    return {
        'social_media': getattr(settings, 'SOCIAL_MEDIA_LINKS', {})
    }
