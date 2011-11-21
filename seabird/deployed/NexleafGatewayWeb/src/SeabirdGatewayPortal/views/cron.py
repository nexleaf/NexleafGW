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


logs_cron_entry = '%s*/5 %s * * * /var/www/seabird/bin/filemover /var/www/seabird/conf/filemover-logs.conf &> /dev/null\n'
audio_cron_entry = '%s*/5 %s * * * /var/www/seabird/bin/filemover /var/www/seabird/conf/filemover-data.conf &> /dev/null\n'
#bulk_get_cron_entry = '%s0,30 %s * * * wget -O /dev/null http://localhost/seabird' + reverse('get_bulk_configs') + ' &> /dev/null\n'
bulk_get_cron_entry = '%s0,30 %s * * * wget -O /dev/null http://localhost/seabird%s &> /dev/null\n'
killfm_cron_entry = '%s*/15 %s * * * /var/www/seabird/bin/killfilemover &> /dev/null\n'


def times_from_cron_string(cronstring):
    retarr = [['%i' % x, '%02i:00' % x, ''] for x in range(0,24)]
    retbool = True
    if cronstring.startswith('#'):
        retbool = False
    else:
        hours = cronstring.split(' ')[1]
        if hours == "*":
            for i in range(len(retarr)):
                retarr[i][2] = 'checked'
        else:
            for i in hours.split(','):
                retarr[int(i)][2] = 'checked'
    return (retarr, retbool)


def times_from_post_list(postlist):
    retarr = [['%i' % x, '%02i:00' % x, ''] for x in range(0,24)]
    retbool = True
    if len(postlist) == 0:
        retbool = False
    else:
        retbool = True
    for i in range(24):
        if str(i) in postlist:
            retarr[i][2] = 'checked'
        else:
            retarr[i][2] = ''
    return (retarr, retbool)

def times_all_checked(alltimes):
    for i in alltimes:
        if i[2] == '':
            return False
    return True

def cron_enabled(is_enabled):
    if is_enabled:
        return ''
    return '#'

def cron_times_from_times(enabled, cron_hours):
    if enabled is False:
        return '*'
    retstr = ''
    first = True
    for i in range(len(cron_hours)):
        if cron_hours[i][2] == 'checked':
            if first:
                retstr += cron_hours[i][0]
                first = False
            else:
                retstr += "," + cron_hours[i][0]
    return retstr


@login_required
def view_cron(request):

    logs_cron_hours = []
    audio_cron_hours = []
    bulk_get_cron_hours = []
    killfm_cron_hours = []
    logs_enabled = True
    audio_enabled = True
    bulk_enabled = True
    killfm_enabled = True
    logs_cron_errors = ''
    audio_cron_errors = ''
    bulk_get_cron_errors = ''
    killfm_cron_errors = ''

    # read the crontab
    (status, output) = commands.getstatusoutput("crontab -l")
    cronlines = output.split('\n')
    for line in cronlines:
        if line.find("filemover-logs") > -1:
            (logs_cron_hours, logs_enabled) = times_from_cron_string(line)

        if line.find("filemover-data") > -1:
            (audio_cron_hours, audio_enabled) = times_from_cron_string(line)

        if line.find("killfilemover") > -1:
            (killfm_cron_hours, killfm_enabled) = times_from_cron_string(line)

        if line.find("wget") > -1:
            (bulk_get_cron_hours, bulk_enabled) = times_from_cron_string(line)

    if request.method == 'POST':
        if 'logs' in request.POST.keys():
            new_hour_list = request.POST.getlist('cron_hours_logs')
            log.info(new_hour_list)
            (logs_cron_hours, logs_enabled) = times_from_post_list(new_hour_list)

        if 'audio' in request.POST.keys():
            new_hour_list = request.POST.getlist('cron_hours_audio')
            log.info(new_hour_list)
            (audio_cron_hours, audio_enabled) = times_from_post_list(new_hour_list)

        if 'killfm' in request.POST.keys():
            new_hour_list = request.POST.getlist('cron_hours_killfm')
            log.info(new_hour_list)
            (killfm_cron_hours, killfm_enabled) = times_from_post_list(new_hour_list)

        cronstring = ''
        cronstring += logs_cron_entry % (cron_enabled(logs_enabled), cron_times_from_times(logs_enabled, logs_cron_hours))
        cronstring += audio_cron_entry % (cron_enabled(audio_enabled), cron_times_from_times(audio_enabled, audio_cron_hours))
        cronstring += killfm_cron_entry % (cron_enabled(killfm_enabled), cron_times_from_times(killfm_enabled, killfm_cron_hours))
        cronstring += bulk_get_cron_entry % (cron_enabled(bulk_enabled), cron_times_from_times(bulk_enabled, logs_cron_hours), reverse('get_bulk_configs'))
        
        tf = tempfile.mktemp()
        fd = open(tf, 'w')
        fd.write(cronstring)
        fd.flush()
        fd.close()
    
        (status, output) = commands.getstatusoutput("crontab -r")
        (status, output) = commands.getstatusoutput("crontab %s" % tf)
        (status, output) = commands.getstatusoutput("crontab -l")
        #os.remove(tf)

    return render_to_response('cron.html', 
        {
            'page_title':'Cron Status',
            'status': status,
            'output': output,
            'logs_cron_hours': logs_cron_hours,
            'audio_cron_hours': audio_cron_hours,
            'killfm_cron_hours': killfm_cron_hours,
            'currdate': datetime.now(),
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
    #if "cronentry" not in request.POST.keys():
    return redirect('/seabird/cron/')
    
    # if request.method == 'POST':
    #     cron_hour_list = request.POST.getlist('cron_hours')
    #     if len(cron_hour_list) > 0:
    #         hour_string = ''
    #         for hour in cron_hour_list:
    #             hour_string += '%s,' % hour
    #         hour_string = hour_string.rstrip(',')
    #     else:
    #         # No hours selected - potentially issue an error message here if 
    #         # at least one must be selected
    #         messages.error(request, FORM_ERROR_MSG)
    #         cron_hour_errors = "At least one hour MUST be selected."
    #         hour_string = '*'
        
    #     # Cron command - do something with it.  (Currently just output to stdout for testing)
    #     cron_time_command = '*/5 %s * * *' % hour_string
    #     print '-'*100
    #     print cron_time_command
    #     print '-'*100

    # thedata = request.POST['cronentry']
    
    # tf = tempfile.mktemp()
    # fd = open(tf, 'w')
    # fd.write(thedata)
    # fd.flush()
    # fd.close()
    
    # (status, output) = commands.getstatusoutput("crontab -r")
    # (status, output) = commands.getstatusoutput("crontab %s" % tf)
    # os.remove(tf)
    
    # return redirect('/seabird/cron/')


    
