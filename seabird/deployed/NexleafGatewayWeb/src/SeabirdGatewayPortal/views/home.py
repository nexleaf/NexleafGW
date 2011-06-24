import sys
import json
import logging
import commands

from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render_to_response
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


@login_required
def releases(request):
    return render_to_response('releases.html', 
        {
            'page_title':'Releases',
        }, context_instance=RequestContext(request))


