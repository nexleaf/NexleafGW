import sys
import json
import logging

from datetime import datetime
import tempfile
import os
import commands
import shutil

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from SeabirdGatewayPortal.utils.postparser import *
from SeabirdGatewayPortal.utils.Logger import getLog

log = getLog('views')
log.setLevel(logging.DEBUG)


# The cell phone expect the following line as an OK signal in the first line
CUSTOMIZED_PHONE_STATUS_OK   = "upok "
CUSTOMIZED_PHONE_STATUS_FAIL = "svrfail "

def get_post_config():
    # (required, type, db_name, default, parser)
    return { \
        "device_id": PostParserArgs(True, "string", "device_id", "None", None), \
        "aux_id": PostParserArgs(False, "string", "aux_id", "", None), \
        "misc": PostParserArgs(False, "string", "misc", "", None), \
        "record_datetime": PostParserArgs(True, "datetime", "record_datetime", datetime.now(), lambda x: datetime.fromtimestamp(float(x)/1000.0)), \
        "gps_latitude": PostParserArgs(False, "float", "gps_latitude", 0.0, None), \
        "gps_longitude": PostParserArgs(False, "float", "gps_longitude", 0.0, None), \
        "gps_altitude": PostParserArgs(False, "float", "gps_altitude", 0.0, None), \
        "mime_type": PostParserArgs(True, "string", "mime_type", "audio/raw", None), \
        "deployment_id": PostParserArgs(True, "string", "deployment_id", "Deployment", None), \
        "version": PostParserArgs(True, "string", "version", "0.0", None), \
        "tag": PostParserArgs(False, "string", "tag", "", None), \
        "data_type": PostParserArgs(True, "string", "data_type", "audio", None)
        }


def upload_get_date_datetime(input_datetime):
    d = input_datetime.date()
    return datetime(d.year, d.month, d.day)




@csrf_exempt
def upload_data(request):

    pp = PostParser(get_post_config())

    strRet = ""
    invalid = False
    invalid_reason = ""
    
    if request.method == 'POST':

        try:

            if 'data' not in request.FILES:
                raise Exception('No file uploaded')

            if 'device_id' not in request.POST:
                raise Exception('No device in upload')
            
            if 'deployment_id' not in request.POST:
                raise Exception('No deployment in upload')

            if 'record_datetime' not in request.POST:
                raise Exception('No record datetime in upload')

            device_id = request.POST['device_id']
            deployment_id = request.POST['deployment_id']
            record_datetime = datetime.fromtimestamp(float(request.POST['record_datetime'])/1000.0)
            datetime_str = record_datetime.strftime("%Y%m%d_%H%M%S")

            # create the filename 
            zipfilename = deployment_id + "_" + device_id + "_" + datetime_str + ".zip"

            workdir_data = tempfile.mkdtemp(dir=settings.DATA_WORK_DIR)
            #workdir_data = workdir_base + "/data/"
            #os.mkdir(workdir_data )
            
            fd = open(workdir_data + "/data.raw", 'w')

            for chunk in request.FILES['data'].chunks():
                fd.write(chunk)
            fd.close()
            
            log.info("JSON dump: " + json.dumps(request.POST))

            fd = open(workdir_data + "/args.json", 'w')
            
            json.dump(request.POST, fd)
            
            fd.close()

            #saved_path = os.getcwd()

            os.chdir(workdir_data)

            (status, output) = commands.getstatusoutput('zip -r -%d %s data.raw args.json' % (settings.ZIP_COMPRESS, zipfilename))

            shutil.move(zipfilename, settings.INCOMING_DIR)

            os.chdir("/var/www/seabird/work")

            (status, output) = commands.getstatusoutput('rm -rf %s' % (workdir_data))

        # handle errors
        except Exception as e:
            log.error("Unknown exception on upload!", exc_info=True)
            strRet = CUSTOMIZED_PHONE_STATUS_FAIL + " -- Unknown exception"
        else:
            strRet = CUSTOMIZED_PHONE_STATUS_OK + " File stored"
    # figure out type, or application, then break
    else:
        log.error('[ Protocol ] Received a non POST request')
        return HttpResponse('Server accepts only HTTP POST messages')

    log.info("Upload result: " + strRet)
    return HttpResponse(content=strRet, mimetype=None, status=200, content_type='text/html')


