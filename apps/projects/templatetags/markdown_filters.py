from django.utils.safestring import mark_safe
from django import template
import markdown

register = template.Library()


@register.filter(name="markdown")
def markdown_to_html(text):
    return mark_safe(markdown.markdown(text))
