from django import template
from django.conf import settings
from django.core.cache import cache
from django.template.defaultfilters import stringfilter
from django.utils.html import urlize as urlize_impl
from django.utils.safestring import mark_safe
from links.models import Link

register = template.Library()


@register.inclusion_tag('links/_object_links.html')
def object_links(object):
    l = Link.objects.for_model(object)
    return {'links': l, 'STATIC_URL': settings.STATIC_URL}


@register.inclusion_tag('links/_object_icon_links.html')
def object_icon_links(obj,show_title=False):
    "Display links as icons, to match the new design"
    key = "%s.%s.%s" % (obj._meta.app_label, obj._meta.module_name, obj.pk)
    l = cache.get(key, None)  # look in the cache first
    if l is None:  # if not found in cache
        l = Link.objects.for_model(obj)  # get it from db
        cache.set(key, l, settings.LONG_CACHE_TIME)  # and save to cache
    return {'links': l, 'show_title': show_title}


@register.filter(is_safe=True, needs_autoescape=True)
@stringfilter
def urlize_target_blank(value, limit=50, autoescape=None):
    return mark_safe(urlize_impl(value,
                                 trim_url_limit=int(limit),
                                 nofollow=True,
                                 autoescape=autoescape).\
                     replace('<a', '<a target="_blank"'))
