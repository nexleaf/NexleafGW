import sys
import json
import logging
import os
import os.path
import stat

from datetime import datetime
from django.http import HttpResponse
from django.template import Context, loader, RequestContext
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.conf import settings
from django.contrib.auth.decorators import login_required

from SeabirdGatewayPortal.utils.Logger import getLog

log = getLog('views')
log.setLevel(logging.DEBUG)



def sort_finfo(a, b):
    return cmp(a['filename'], b['filename'])

@login_required
def view_incoming(request):

    indir = settings.INCOMING_DIR
    filelist = os.listdir(indir)
    nowsec = int(datetime.now().strftime("%s"))
    
    allfiles = []
    for f in filelist:
        s = os.stat(indir + f)
        finfo = { \
            "filename": f, \
            "date": datetime.fromtimestamp(s.st_ctime), \
            "oldmin": (nowsec - s.st_ctime) / 60.0, \
            "size": s.st_size }
        allfiles.append(finfo)

    sfiles = sorted(allfiles, cmp=sort_finfo)

    paginator = Paginator(sfiles, 50)

    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    try:
        incout = paginator.page(page)
    except (EmptyPage, InvalidPage):
        incout = paginator.page(paginator.num_pages)

    
    t = loader.get_template('files.html')
    c = RequestContext(request, {'incout': incout, 'totalfiles': len(sfiles)})
    return HttpResponse(t.render(c))

@login_required
def view_incoming_grid(request):
    
    indir = settings.INCOMING_DIR
    filelist = os.listdir(indir)
    
    allsta = []
    alldates = []
    for f in filelist:
        if not f.endswith("zip"):
            continue

        #SEFI2011_A1000017EBA720_20110824_010015.zip
	fsp = f.split('_')
        fdate = fsp[2]
        fsta = fsp[1]
        if fdate not in alldates:
            alldates.append(fdate)
        if fsta not in allsta:
            allsta.append(fsta)

    alldates.sort()

    datelookup = {}
    for i in range(len(alldates)):
        datelookup[alldates[i]] = i

    alldata = {}

    totaldata = 0

    for sta in allsta:
        dd = []
        for dt in alldates:
            dd.append({'date': dt, 'audio': 0, 'logs': 0})
        alldata[sta] = {'sta': sta, 'daydata': dd}


    for f in filelist:
        if not f.endswith("zip"):
            continue

	fsp = f.split('_')
        fdate = fsp[2]
        fsta = fsp[1]
        s = os.stat(indir + f)

        totaldata += s.st_size

        if s.st_size > 150000:
            alldata[fsta]['daydata'][datelookup[fdate]]['audio'] += 1
        else:
            alldata[fsta]['daydata'][datelookup[fdate]]['logs'] += 1
        
    t = loader.get_template('files_grid.html')
    c = RequestContext(request, {'dates': alldates, 'devdata': alldata.values(), 'totalfiles': len(filelist), 'totaldata': totaldata})
    return HttpResponse(t.render(c))


            
