from django import template

register = template.Library()


@register.filter
def split_commas(value):
    """Split a comma-separated string into a list of trimmed, non-empty parts.

    Used for fields like Property.outdoor_areas where the admin enters
    'Garden 52 m², Pool area 110 m²' and the template renders each as a row.
    """
    if not value:
        return []
    return [part.strip() for part in str(value).split(",") if part.strip()]