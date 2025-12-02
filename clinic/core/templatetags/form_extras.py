from django import template

register = template.Library()


@register.filter
def add_class(field, css):
    """
    Usage in templates:
    {{ form.field_name|add_class:"form-control" }}
    """
    existing = field.field.widget.attrs.get("class", "")
    classes = f"{existing} {css}".strip()
    attrs = {**field.field.widget.attrs, "class": classes}
    return field.as_widget(attrs=attrs)


