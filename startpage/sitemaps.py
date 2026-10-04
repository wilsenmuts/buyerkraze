from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Article, Event
from .seo import site_host


class _Base(Sitemap):
    protocol = 'https'

    def get_domain(self, site=None):
        return site_host()


class StaticSitemap(_Base):
    changefreq = 'weekly'

    PRIORITIES = {'start': 1.0, 'article_list': 0.8, 'event_list': 0.8, 'privacy': 0.3, 'terms': 0.3}

    def items(self):
        return list(self.PRIORITIES)

    def location(self, item):
        return reverse(item)

    def priority(self, item):
        return self.PRIORITIES[item]


class ArticleSitemap(_Base):
    changefreq = 'monthly'
    priority = 0.7

    def items(self):
        return Article.objects.all()

    def lastmod(self, obj):
        return obj.updated_date

    def location(self, obj):
        return reverse('article_detail', args=[obj.pk])


class EventSitemap(_Base):
    changefreq = 'weekly'
    priority = 0.6

    def items(self):
        return Event.objects.all()

    def location(self, obj):
        return reverse('event_detail', args=[obj.pk])
