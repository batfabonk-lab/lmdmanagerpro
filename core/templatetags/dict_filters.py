from django import template

register = template.Library()

@register.filter
def lookup(dictionary, key):
    """
    Returns the value for a given key from a dictionary.
    """
    if dictionary is None:
        return None
    return dictionary.get(key)
