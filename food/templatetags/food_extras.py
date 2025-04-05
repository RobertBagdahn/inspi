from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Get an item from a dictionary using the key.
    
    Usage in template:
    {{ mydict|get_item:item_key }}
    """
    if dictionary is None:
        return None
    return dictionary.get(key)
