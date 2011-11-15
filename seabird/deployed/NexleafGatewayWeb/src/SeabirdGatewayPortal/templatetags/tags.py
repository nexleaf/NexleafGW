from django.conf import settings
from django import template

import re

# COMMON TAGS - Used sitewide.
# IMPORTANT - These are loaded "globally" - via SeabirdGatewayPortal/__init__.py add_to_builtins
register = template.Library()

# Determine if tab is active
@register.simple_tag
def active(request, pattern):
    if re.search(pattern, request.path_info):
        return 'active'
    return ''


@register.inclusion_tag('format/form_field.html', takes_context=True)
def form_field(context, field, field_class=''):
    '''
        Simple inclusion tag for rendering customizable form fields.
    '''
    context = {
        'field':field, 
        'field_class': field_class,
    }
    return context

