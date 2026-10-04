import json
from urllib.parse import urlparse

from django.conf import settings
from django.urls import reverse
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from django.utils.text import Truncator

SITE_NAME = 'BuyerKraze'
TAGLINE = 'The reverse marketplace where buyers post what they want and the price they will pay, and sellers compete to fulfil it.'

FAQS = [
    ('What is BuyerKraze?',
     'BuyerKraze is a reverse marketplace. Instead of searching through listings, buyers post what they want '
     'and the price they are willing to pay, and sellers browse those offers and choose the ones they can fulfil.'),
    ('How does a reverse marketplace work?',
     'A buyer publishes an offer describing the product or service they need and their target price. '
     'Sellers browse the offers, accept the ones that suit them or negotiate terms, and express interest directly to the buyer.'),
    ('How do buyers use BuyerKraze?',
     'Choose your country, create an offer with the item you want and the price you will pay, then review the sellers who '
     'express interest and pick the deal that works best for you.'),
    ('How do sellers use BuyerKraze?',
     'Sellers browse buyer offers in their country, accept an offer at the stated price, negotiate a better fit, '
     'or express interest in supplying the product.'),
    ('Is BuyerKraze free to use?',
     'Browsing the site, reading articles and viewing events is free. See the Terms and Conditions for the current rules on accounts and fees.'),
    ('Which countries does BuyerKraze serve?',
     'BuyerKraze runs a dedicated site for each supported country. Choose your country on the home page, or let BuyerKraze '
     'detect your location, to be taken to your local BuyerKraze marketplace.'),
]


def site_url():
    return getattr(settings, 'SITE_URL', 'https://buyerkraze.com').rstrip('/')


def site_host():
    return urlparse(site_url()).netloc


def abs_url(path_or_url):
    if not path_or_url:
        return ''
    if path_or_url.startswith(('http://', 'https://')):
        return path_or_url
    return site_url() + (path_or_url if path_or_url.startswith('/') else '/' + path_or_url)


def default_image():
    return abs_url(settings.STATIC_URL + 'hero/og_image.jpg')


def summarize(text, words=28):
    return Truncator(' '.join(strip_tags(text or '').split())).words(words, truncate='…')


def jsonld(data):
    """Serialise to a script-safe JSON string for a ld+json block."""
    raw = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
    return mark_safe(raw.replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026'))


def site_graph():
    same_as = [u for u in getattr(settings, 'SOCIAL_MEDIA_LINKS', {}).values() if u and u.startswith('http')]
    return {
        '@context': 'https://schema.org',
        '@graph': [
            {
                '@type': 'Organization',
                '@id': site_url() + '/#organization',
                'name': SITE_NAME,
                'url': site_url() + '/',
                'logo': {
                    '@type': 'ImageObject',
                    'url': abs_url(settings.STATIC_URL + 'images/icon/android-chrome-512x512.png'),
                    'width': 512, 'height': 512,
                },
                'description': TAGLINE,
                'sameAs': same_as,
            },
            {
                '@type': 'WebSite',
                '@id': site_url() + '/#website',
                'url': site_url() + '/',
                'name': SITE_NAME,
                'description': TAGLINE,
                'inLanguage': 'en',
                'publisher': {'@id': site_url() + '/#organization'},
            },
        ],
    }


def faq_schema():
    return {
        '@context': 'https://schema.org',
        '@type': 'FAQPage',
        'mainEntity': [
            {'@type': 'Question', 'name': q,
             'acceptedAnswer': {'@type': 'Answer', 'text': a}}
            for q, a in FAQS
        ],
    }


def breadcrumbs(items):
    """items: list of (name, path)."""
    return {
        '@context': 'https://schema.org',
        '@type': 'BreadcrumbList',
        'itemListElement': [
            {'@type': 'ListItem', 'position': i, 'name': name, 'item': abs_url(path)}
            for i, (name, path) in enumerate(items, 1)
        ],
    }


def article_schema(article):
    url = abs_url(reverse('article_detail', args=[article.pk]))
    image = article.top_image or article.featured_image
    author_name = (article.author.get_full_name() or article.author.get_username()) if article.author else SITE_NAME
    data = {
        '@context': 'https://schema.org',
        '@type': 'Article',
        'mainEntityOfPage': {'@type': 'WebPage', '@id': url},
        'headline': Truncator(article.title).chars(110),
        'description': summarize(article.content),
        'datePublished': article.published_date.isoformat(),
        'dateModified': article.updated_date.isoformat(),
        'author': {'@type': 'Person' if article.author else 'Organization', 'name': author_name},
        'publisher': {'@id': site_url() + '/#organization'},
        'inLanguage': 'en',
    }
    if image:
        data['image'] = [abs_url(image.url)]
    return data


def event_schema(event):
    url = abs_url(reverse('event_detail', args=[event.pk]))
    data = {
        '@context': 'https://schema.org',
        '@type': 'Event',
        'name': event.title,
        'description': summarize(event.description, 40),
        'startDate': event.event_date.isoformat(),
        'eventAttendanceMode': 'https://schema.org/MixedEventAttendanceMode',
        'eventStatus': 'https://schema.org/EventScheduled',
        'location': {
            '@type': 'Place',
            'name': event.location or event.country_region,
            'address': event.country_region,
        },
        'organizer': {'@type': 'Organization', 'name': SITE_NAME, 'url': site_url() + '/'},
        'url': url,
    }
    if event.featured_image:
        data['image'] = [abs_url(event.featured_image.url)]
    return data
