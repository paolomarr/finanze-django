from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
@stringfilter
def split(value, arg):
    return value.split(arg)

@register.filter
def divide(value, arg):
    try:
        dividend = float(value)
        divisor = float(arg)
        return dividend / divisor
    except Exception:
        return "ERR"
