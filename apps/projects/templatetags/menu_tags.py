from django import template
from django.urls import reverse

register = template.Library()

@register.simple_tag(takes_context=True)
def active(context, url):
    """
    Returns "active" if the request path starts with the given prefix, otherwise returns an empty string.
    - `prefix`: The URL prefix to check against the request path.
    """
    request = context.get('request')
    is_active = request and request.path == url
    return "active" if is_active else ""


@register.simple_tag(takes_context=True)
def project_active(context, url, pk):
    """
    Returns "active" if the request path starts with the given prefix, otherwise returns an empty string.
    - `prefix`: The URL prefix to check against the request path.
    """
    request = context.get('request')
    is_active = request and request.path == reverse(url, kwargs={'pk':pk})
    return "active" if is_active else ""
