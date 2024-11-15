from django import template
from django.urls import reverse

register = template.Library()

@register.simple_tag(takes_context=True)
def active(context, url, output="active"):
    """
    Returns "active" if the request path starts with the given prefix, otherwise returns an empty string.
    - `prefix`: The URL prefix to check against the request path.
    """
    request = context.get('request')
    is_active = request and request.path == url
    return output if is_active else ""


@register.simple_tag(takes_context=True)
def project_active(context, url, pk, output="active"):
    """
    Returns "active" if the request path starts with the given prefix, otherwise returns an empty string.
    - `prefix`: The URL prefix to check against the request path.
    """
    request = context.get('request')
    is_active = request and request.path == reverse(url, kwargs={'pk':pk})
    return output if is_active else ""
