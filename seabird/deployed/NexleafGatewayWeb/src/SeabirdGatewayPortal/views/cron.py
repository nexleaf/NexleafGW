import sys
import json
import logging
import os
import os.path
import stat
import commands
import tempfile

from datetime import datetime
from django.http import HttpResponse
from django.template import Context, loader, RequestContext
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.conf import settings
from django.contrib.auth.decorators import login_required

from django.shortcuts import redirect

from SeabirdGatewayPortal.utils.Logger import getLog

log = getLog('views')
log.setLevel(logging.DEBUG)


@login_required
def view_cron(request):

    (status, output) = commands.getstatusoutput("crontab -l")

    if status == 0:
        default = output
    else:
        default = "# m h  dom mon dow   command\n*/5 * * * * /var/www/seabird/bin/filemover &> /dev/null"
    
    t = loader.get_template('cron.html')
    c = RequestContext(request, {'status': status, 'output': output, 'default': default})
    return HttpResponse(t.render(c))

@login_required
def toggle_default_cron(request):

    (status, output) = commands.getstatusoutput("crontab -l")

    if status == 0:
        (status, output) = commands.getstatusoutput("crontab -r")
    else:
        (status, output) = commands.getstatusoutput("crontab %s" % settings.CRON_FILE)
    
    return redirect('/seabird/cron/')

@login_required
def set_cron(request):

    if "cronentry" not in request.POST.keys():
        return redirect('/seabird/cron/')

    thedata = request.POST['cronentry']

    tf = tempfile.mktemp()
    fd = open(tf, 'w')
    fd.write(thedata)
    fd.flush()
    fd.close()

    (status, output) = commands.getstatusoutput("crontab -r")
    (status, output) = commands.getstatusoutput("crontab %s" % tf)

    return redirect('/seabird/cron/')


    
