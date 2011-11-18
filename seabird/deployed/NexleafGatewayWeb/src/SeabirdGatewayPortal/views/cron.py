import sys
import json
import logging
import os
import os.path
import stat
import commands
import tempfile

from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import redirect, render_to_response
from django.template import Context, loader, RequestContext

from SeabirdGatewayPortal.common.constants import FORM_ERROR_MSG
from SeabirdGatewayPortal.utils.Logger import getLog

log = getLog('views')
log.setLevel(logging.DEBUG)


@login_required
def view_cron(request):
    # For cron checkboxes (values, displayed_values)
    cron_hour_choices = [('%i' % x, '%02i:00' % x) for x in range(0,24)]
    cron_hour_errors = ''
    if request.method == 'POST':
        cron_hour_list = request.POST.getlist('cron_hours')
        if len(cron_hour_list) > 0:
            hour_string = ''
            for hour in cron_hour_list:
                hour_string += '%s,' % hour
            hour_string = hour_string.rstrip(',')
        else:
            # No hours selected - potentially issue an error message here if 
            # at least one must be selected
            messages.error(request, FORM_ERROR_MSG)
            cron_hour_errors = "At least one hour MUST be selected."
            hour_string = '*'
        
        # Cron command - do something with it.  (Currently just output to stdout for testing)
        cron_time_command = '* %s * * *' % hour_string
        print '-'*100
        print cron_time_command
        print '-'*100
        
    # Cron retrieval and management.
    (status, output) = commands.getstatusoutput("crontab -l")
    if status == 0:
        default = output
    else:
        default = '# m h  dom mon dow   command\n' + \
            '*/5 * * * * /var/www/seabird/bin/filemover /var/www/seabird/conf/filemover-logs.conf &> /dev/null\n' + \
            '*/5 * * * * /var/www/seabird/bin/filemover /var/www/seabird/conf/filemover-data.conf &> /dev/null\n' + \
            '0,30 * * * * wget -O /dev/null http://localhost/seabird%s &> /dev/null\n' % reverse('get_bulk_configs') + \
            '0,30 6 * * * /var/www/seabird/bin/killfilemover &> /dev/null'
        default = '' # overridden for local development.
    
    return render_to_response('cron.html', 
        {
            'page_title':'Cron Status',
            'status': status,
            'output': output,
            'default': default,
            'cron_hour_choices':cron_hour_choices,
            'cron_hour_errors':cron_hour_errors,
        }, context_instance=RequestContext(request))


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


    
