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

