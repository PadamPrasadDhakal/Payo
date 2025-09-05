from django import template


register = template.Library()


@register.filter(name="add_class")
def add_class(bound_field, css_classes: str):
    existing = bound_field.field.widget.attrs.get("class", "")
    merged = (existing + " " + css_classes).strip()
    attrs = {**bound_field.field.widget.attrs, "class": merged}
    return bound_field.as_widget(attrs=attrs)


