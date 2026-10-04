from django.conf import settings

def social_media_links(request):
    """Make social media links available to all templates"""
    return {
        'social_media': getattr(settings, 'SOCIAL_MEDIA_LINKS', {})
    }


def seo(request):
    from . import seo as s
    return {
        'site_url': s.site_url(),
        'seo_default_image': s.default_image(),
        'canonical_default': s.site_url() + request.path,
        'jsonld_site': s.jsonld(s.site_graph()),
        'google_site_verification': getattr(settings, 'GOOGLE_SITE_VERIFICATION', ''),
        'bing_site_verification': getattr(settings, 'BING_SITE_VERIFICATION', ''),
    }
