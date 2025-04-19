from urllib.parse import urlencode
from django import template
from django.db.models import Sum, Avg, Max, Min, Count

register = template.Library()


@register.simple_tag(takes_context=True)
def updated_params(context, **kwargs):
    dict_ = context["request"].GET.copy()
    for k, v in kwargs.items():
        dict_[k] = v
    return dict_.urlencode()


@register.filter
def approved(comments):
    return comments.filter(is_approved=True)


@register.filter
def sum(queryset, field):
    return queryset.aggregate(sum_value=Sum(field)).get("sum_value")


@register.filter
def avg(queryset, field):
    return queryset.aggregate(avg_value=Avg(field)).get("avg_value")


@register.filter
def min(queryset, field):
    return queryset.aggregate(min_value=Min(field)).get("min_value")


@register.filter
def max(queryset, field):
    return queryset.aggregate(max_value=Max(field)).get("max_value")


@register.filter
def count(queryset, field):
    return queryset.aggregate(count_value=Count(field)).get("count_value")


@register.filter
def multiply(value1, value2):
    """
    Multiplies all values in the specified field.
    Returns None if the queryset is empty.
    """
    from django.db.models import F, ExpressionWrapper, FloatField
    from functools import reduce
    import operator

    if value1 is None or value2 is None:
        return None

    # Convert string values with commas to float
    try:
        v1 = float(str(value1).replace(",", "."))
        v2 = float(str(value2).replace(",", "."))
        return v1 * v2
    except (ValueError, TypeError):
        return None


@register.filter
def divide(value1, value2):
    """
    Divides value1 by value2.
    Returns None if value2 is zero or if any value is None.
    """
    if value1 is None or value2 is None:
        return None

    # Convert string values with commas to float
    try:
        v1 = float(str(value1).replace(",", "."))
        v2 = float(str(value2).replace(",", "."))
        if v2 == 0:
            return None
        return v1 / v2
    except (ValueError, TypeError):
        return None


@register.filter
def abs_value(value):
    """
    Returns the absolute value of the given value.
    Returns None if the value is None or cannot be converted to a number.
    """
    if value is None:
        return None

    try:
        # Convert string values with commas to float
        v = float(str(value).replace(",", "."))
        return abs(v)
    except (ValueError, TypeError):
        return None


@register.filter
def get_item(dictionary, key):
    """
    Returns the value from a dictionary for the given key.
    Returns None if the key doesn't exist or if the dictionary is None.
    """
    if dictionary is None:
        return None

    try:
        return dictionary.get(key)
    except (AttributeError, TypeError):
        try:
            return dictionary[key]
        except (KeyError, TypeError):
            return None


@register.filter
def get_item_by_index(list_object, index):
    """
    Returns the item at the specified index from a list or queryset.
    Returns None if the index is out of range or if the object is not a list-like object.
    """
    if list_object is None:
        return None
    
    try:
        index = int(index)
        return list_object[index]
    except (IndexError, TypeError, ValueError):
        return None
    


@register.filter
def typename(value):
    """
    Returns the type name of the given value.
    """
    return type(value).__name__


