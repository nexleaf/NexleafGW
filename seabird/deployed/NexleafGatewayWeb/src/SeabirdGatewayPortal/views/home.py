import sys
import json
import logging
import commands

from datetime import datetime
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.template import Context, loader, RequestContext

from SeabirdGatewayPortal.utils.Logger import getLog

log = getLog('views')
log.setLevel(logging.DEBUG)

def home(request):
    log.info("home page access")
    
    (status, output) = commands.getstatusoutput("uptime")
    t = loader.get_template('home.html')
    c = RequestContext(request, {'yes': True, 'output': output})
    return HttpResponse(t.render(c))




