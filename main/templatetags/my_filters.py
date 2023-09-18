from django import template
import django
register = template.Library()

@register.filter
def set_id(field, id):
    print(id)
    if isinstance(field, django.forms.Field):
        return field.as_widget(attrs={'id': id})
    return field

from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()
import ast,json
@register.filter
# @stringfilter
def upto(value ):
    
    print(','.join([str(i) for i in value]))
    return ','.join([str(i) for i in value])
# upto.is_safe = True


