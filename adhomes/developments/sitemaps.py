"""Sitemaps for /sitemap.xml.

URLs are built from the Sites framework domain (adhomeshelder.com, set in
adhomes/contrib/sites/migrations/0003) and served over https.
"""

from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Project, Property


class StaticViewSitemap(Sitemap):
    protocol = "https"
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        return [
            "developments:home",
            "about",
            "developments:project_list",
            "developments:property_list",
            "developments:contact",
        ]

    def location(self, item):
        return reverse(item)


class ProjectSitemap(Sitemap):
    protocol = "https"
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Project.objects.order_by("order", "-created")

    def lastmod(self, obj):
        return obj.updated


class PropertySitemap(Sitemap):
    protocol = "https"
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Property.objects.order_by("order", "name")

    def lastmod(self, obj):
        return obj.updated


sitemaps = {
    "static": StaticViewSitemap,
    "projects": ProjectSitemap,
    "properties": PropertySitemap,
}
