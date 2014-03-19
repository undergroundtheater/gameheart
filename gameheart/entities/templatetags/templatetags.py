#templatetags

from django import template

register = template.Library()

def hash(d, key):
    return d[key]

def dot(d, key):
    return getattr(d,key)

def iloop(value):
    return range(value)

def toint(value):
    try:
        int(value)
        return int(value)
    except ValueError:
        return value

register.filter(hash)
register.filter(dot)
register.filter(iloop)
register.filter(toint)
