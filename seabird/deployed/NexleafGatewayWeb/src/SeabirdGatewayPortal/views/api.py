import logging, socket, sys, urllib2

from datetime import datetime, timedelta
from xml.dom import minidom

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext

from mongoengine import connect
from mongoengine.django.shortcuts import get_document_or_404

from SeabirdGatewayPortal.Collections.Config import Config
from SeabirdGatewayPortal.Collections.Device import Device

from SeabirdGatewayPortal.utils.Logger import getLog

# Connect to MongoDB - Gateway.
connect('SeabirdGWDB')

log = getLog('views')
log.setLevel(logging.DEBUG)

# Set default timeout so requests don't hang for too long 
# and create spinning processes on gateway server.
socket.setdefaulttimeout(10.0)

def get_bulk_configs(request):
    # Grab bulk data from primary server.
    try:
        response = urllib2.urlopen(settings.BULK_CONFIGS_URL)
        parsed_xml = minidom.parseString(response.read())
    except Exception:
        # URLError, HTTPError, XML Parsing Error, or other Errors possible.  
        # Log the error and exit.
        e = sys.exc_info()[1]
        log.error('ERROR: %s' % e)
        return HttpResponse('ERROR. %s' % s)
    
    all_configs = parsed_xml.getElementsByTagName('Configuration')
    for c in all_configs:
        # Get or create the configuration.
        config_title = c.getElementsByTagName('Name')[0].firstChild.data.strip()
        config_xml = c.toxml()
        config_version = c.getElementsByTagName('Version')[0].firstChild.data.strip()
        
        try:
            # Find existing config - Version is Unique!
            config = Config.objects.get(version=config_version)
        except Config.DoesNotExist:
            config = Config(version=config_version)
        
        # Update title and xml regardless if new or edit based on changes from server.
        # Version might remain the same, but other parameters could have changed.
        config.title = config_title
        config.xml = config_xml
        config.save()
        
        # Get or create the device associated with this configuration.
        device_id = c.getAttribute('assignToDeviceId').strip()
        try:
            # Find existing config - Version is Unique!
            device = Device.objects.get(device_id=device_id)
        except Device.DoesNotExist:
            device = Device(device_id=device_id)
        
        device.config = config
        device.save()
    
    return HttpResponse('Success!')


