'''
This template tag takes a shortcode and returns a more familiar version
e.g 255 will become *255#
'''
from django.utils.safestring import mark_safe
from django import template

register = template.Library()


@register.filter(is_safe=True)
def readable(shortcode):
    new_code = str(shortcode)
    if new_code[0] != "*":
        new_code = f"*{shortcode}#"
    return mark_safe(new_code)
