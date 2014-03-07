#templatetags

from django import template

register = template.Library()

def hash(d, key):
    return d[key]

def dot(d, key):
    return getattr(d,key)

register.filter(hash)
register.filter(dot)
