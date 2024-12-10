from activity.activity.models import Activity

from django.contrib.sitemaps import Sitemap



class ActivitySitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return Activity.objects.filter(status='2')

    def lastmod(self, obj):
        return obj.created_at