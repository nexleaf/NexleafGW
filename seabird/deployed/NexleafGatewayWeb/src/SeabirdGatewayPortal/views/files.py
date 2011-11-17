import sys
import json
import logging
import os
import os.path
import stat
import gzip
import zipfile
import tempfile

from datetime import date
from datetime import datetime
from datetime import timedelta
from django.http import HttpResponse, HttpResponseNotFound, Http404
from django.template import Context, loader, RequestContext
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.conf import settings
from django.contrib.auth.decorators import login_required
from mongoengine.django.shortcuts import get_document_or_404

from SeabirdGatewayPortal.Collections.Config import Config
from SeabirdGatewayPortal.Collections.Device import Device
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
def get_record_log(request, device_id=None, viewdate=None):
    if device_id == None:
        return HttpResponseNotFound()
    if viewdate == None:
        return HttpResponseNotFound()
    
    thedate = datetime.strptime(viewdate, '%Y%m%d%H%M%S')
    datedir = thedate.strftime('%Y/%m/%d')
    searchdate = thedate.strftime('%Y%m%d_%H%M%S')

    logindir = os.path.normpath(settings.INCOMING_DIR) + "/logs/" + datedir
    
    logfiles = []
    if os.path.exists(logindir):
        logfiles = os.listdir(logindir)

    foundfile = ''
    for f in logfiles:
        if f.find(device_id) > -1 and f.find(searchdate) > -1:
            foundfile = f

    if foundfile == '':
        return HttpResponseNotFound('File not found! 1')

    fullfile = logindir + "/" + foundfile
    if not os.path.exists(fullfile):
        return HttpResponseNotFound('File not found! 2')

    zf = zipfile.ZipFile(fullfile, mode='r')
    if 'data.raw' not in zf.namelist():
        zf.close()
        return HttpResponseNotFound('No data in zip file!')
    
    (fd, name) = tempfile.mkstemp(dir="/tmp/")
    fd = open(name, 'w')
    zfd = zf.open('data.raw')
    fd.write(zfd.read())
    fd.flush()
    fd.close()
    zfd.close()
    zf.close()
    
    #gzf = gzip.GzipFile(fileobj=zf.open('data.raw'), mode='rb')
    gzf = gzip.GzipFile(filename=name, mode='rb')
    response = HttpResponse(mimetype="text/plain")
    #response['Content-Disposition'] = 'attachment; filename=' + upload_list[0].file.get().name.replace('/','_').replace(".raw", ".wav")
    response.write(gzf.read())
    gzf.close()
    os.remove(name)
    
    return response
    
    


def get_total_sizes(directory, filelist):
    retsize = 0
    for f in filelist:
        st = os.stat(directory + "/" + f)
        retsize += st.st_size
    return retsize


@login_required
def view_device_day(request, device_id=None, viewdate=None):
    if device_id == None:
        return HttpResponseNotFound()
    if viewdate == None:
        return HttpResponseNotFound()

    dev = get_document_or_404(Device, device_id=device_id)
    
    thedate = datetime.strptime(viewdate, '%Y%m%d')
    datedir = thedate.strftime('%Y/%m/%d')

    dataindir = os.path.normpath(settings.INCOMING_DIR) + "/data/" + datedir
    logindir = os.path.normpath(settings.INCOMING_DIR) + "/logs/" + datedir

    datafiles = []
    logfiles = []
    if os.path.exists(dataindir):
        datafiles = os.listdir(dataindir)
    if os.path.exists(logindir):
        logfiles = os.listdir(logindir)

    stadata = []
    for f in datafiles:
        if f.find(device_id) > -1:
            stadata.append(f)
    logdata = []
    for f in logfiles:
        if f.find(device_id) > -1:
            logdata.append(f)
    
    stadata.sort()
    logdata.sort()
    
    alldata = []
    if len(stadata) > 0:
        seconds20 = timedelta(seconds=20)
        fd_list = stadata[0].split('.')[0].split('_')[-2:]
        basedate = datetime.strptime(fd_list[0] + '_' + fd_list[1], '%Y%m%d_%H%M%S')
        basefile = stadata[0]
        prevdate = datetime.strptime(fd_list[0] + '_' + fd_list[1], '%Y%m%d_%H%M%S')
        filecount = 1
        for i in range(1, len(stadata)):
            fd_list = stadata[i].split('.')[0].split('_')[-2:]
            currdate = datetime.strptime(fd_list[0] + '_' + fd_list[1], '%Y%m%d_%H%M%S')
            if currdate - prevdate < seconds20:
                filecount += 1
                prevdate = currdate
            else:
                st = os.stat(dataindir + "/" + basefile)
                alldata.append({'date': basedate.strftime('%Y/%m/%d %H:%M:%S'), 'mins': filecount / 4.0,
                                'created': datetime.fromtimestamp(st.st_ctime).strftime('%Y/%m/%d %H:%M:%S')})
                basedate=currdate
                prevdate = currdate
                filecount = 1
                basefile = stadata[i]
    
    alllogs = []
    if len(logdata) > 0:
        for f in logdata:
            st = os.stat(logindir + "/" + f)
            fd_str = f.split('.')[0].split('_')[-2:]
            fd = datetime.strptime(fd_str[0] + '_' + fd_str[1], '%Y%m%d_%H%M%S')
            alllogs.append({'date': fd, 'size': st.st_size, 
                            'created': datetime.fromtimestamp(st.st_ctime).strftime('%Y/%m/%d %H:%M:%S')})



    t = loader.get_template('files_device_day.html')
    c = RequestContext(request, {
        'dev': dev,
        'alldata': alldata,
        'alllogs': alllogs,
        'page_title':'Data for %s on %s' % (dev, datedir),
    })
    return HttpResponse(t.render(c))
    


@login_required
def view_incoming_grid(request, startdate=None):
    #
    # TODO: forward and back browsing!
    #
    dataindir = os.path.normpath(settings.INCOMING_DIR) + "/data"
    logindir = os.path.normpath(settings.INCOMING_DIR) + "/logs"
    
    datalist_gen = os.walk(dataindir)
    loglist_gen = os.walk(logindir)
    
    startday = None
    stopday = None
    if startdate is not None:
        startday = datetime.strptime(startdate, "%Y%m%d").date()
        stopday = startday + timedelta(days=8)
    else:
        startday = date.today() + timedelta(days=1) - timedelta(days=8)
        stopday = startday + timedelta(days=8)

    totaldata = 0
    totallogs = 0
    diskusage = 0
    
    datelist = []
    stalist = []
    datadict = {}
    logdict = {}

    # data
    for (thedir, dirs, files) in datalist_gen:
        if len(files) == 0:
            continue
        
        # get aggregates
        totaldata += len(files)
        diskusage += get_total_sizes(thedir, files)
        
        # what date are we working on
        ymd = files[0].split('.')[0].split('_')[-2]
        filedate = datetime.strptime(ymd, '%Y%m%d').date()
        if filedate > stopday or filedate < startday:
            continue

        if ymd not in datelist:
            datelist.append(ymd)

        tempstalist = []

        for f in files:
            sta = f.split('.')[0].split('_')[-3]
            tempstalist.append(sta)
            if sta not in stalist:
                stalist.append(sta)

        log.info("D ymd: %s filecnd: %d" % (ymd, len(tempstalist)))

        if ymd in datadict.keys():
            datadict[ymd].extend(tempstalist)
        else:
            datadict[ymd] = tempstalist
    
    # logs
    for (thedir, dirs, files) in loglist_gen:
        if len(files) == 0:
            continue
        
        # get aggregates
        totallogs += len(files)
        diskusage += get_total_sizes(thedir, files)
        
        # what date are we working on
        ymd = files[0].split('.')[0].split('_')[-2]
        filedate = datetime.strptime(ymd, '%Y%m%d').date()
        if filedate > stopday or filedate < startday:
            continue

        if ymd not in datelist:
            datelist.append(ymd)

        tempstalist = []

        for f in files:
            sta = f.split('.')[0].split('_')[-3]
            tempstalist.append(sta)
            if sta not in stalist:
                stalist.append(sta)

        log.info("L ymd: %s filecnt: %d" % (ymd, len(tempstalist)))

        if ymd in logdict.keys():
            logdict[ymd].extend(tempstalist)
        else:
            logdict[ymd] = tempstalist
            
    datelist.sort()
    stalist.sort()
    alllist = []
    for sta in stalist:
        dev = get_document_or_404(Device, device_id=sta)
        appd = {'sta': sta, 'staprn': dev, 'counts': []}
        for ldate in datelist:
            data = 0
            logs = 0
            if ldate in datadict.keys():
                data = datadict[ldate].count(sta)
            if ldate in logdict.keys():
                logs = logdict[ldate].count(sta)
            appd['counts'].append({'data': data, 'logs': logs, 'date': ldate})
        alllist.append(appd)

    log.info('%s' % (alllist))

    t = loader.get_template('files_grid.html')
    c = RequestContext(request, {
        'dates': datelist,
        'allfiles': alllist,
        'totaldata': totaldata,
        'totallogs': totallogs,
        'diskusage': diskusage,
        'page_title':'Files Ready To Send'
    })
    return HttpResponse(t.render(c))
        
    

@login_required
def view_incoming_grid_old(request):
    
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
    c = RequestContext(request, {
        'dates': alldates,
        'devdata': alldata.values(),
        'totalfiles': len(filelist),
        'totaldata': totaldata,
        'page_title':'In / Out Files'
    })
    return HttpResponse(t.render(c))


            
