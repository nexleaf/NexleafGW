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
from django.core.urlresolvers import reverse
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
        default = '# m h  dom mon dow   command\n' + \
            '*/5 * * * * /var/www/seabird/bin/filemover /var/www/seabird/conf/filemover-logs.conf &> /dev/null\n' + \
            '*/5 * * * * /var/www/seabird/bin/filemover /var/www/seabird/conf/filemover-data.conf &> /dev/null\n' + \
            '0,30 * * * * wget -O /dev/null http://localhost/seabird%s &> /dev/null\n' % reverse('get_bulk_configs') + \
            '0,30 6 * * * /var/www/seabird/bin/killfilemover &> /dev/null'
    
    t = loader.get_template('cron.html')
    c = RequestContext(request, {
        'status': status,
        'output': output,
        'default': default,
        'page_title':'Cron Status'})
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


    
