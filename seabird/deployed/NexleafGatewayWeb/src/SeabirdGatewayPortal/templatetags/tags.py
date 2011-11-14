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

