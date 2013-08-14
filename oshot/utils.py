from django.conf import settings
from django.contrib.sites.models import Site

def get_root_url():
    site = Site.objects.get(pk=settings.SITE_ID)
    return 'http://' + site.domain

