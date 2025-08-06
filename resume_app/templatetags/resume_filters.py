from django import template

register = template.Library()

@register.filter(name='mul')
def mul(value, arg):
    """Multiply the arg by the value."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return ''