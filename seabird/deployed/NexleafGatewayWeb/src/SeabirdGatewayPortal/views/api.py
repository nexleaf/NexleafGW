import cgi, logging, os, socket, sys, urllib2

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

from SeabirdGatewayPortal.Collections.Config import Config, ConfigRequestCache
from SeabirdGatewayPortal.Collections.Device import Device

from SeabirdGatewayPortal.utils.Logger import getLog

# Connect to MongoDB - Gateway.
connect('SeabirdGWDB')

log = getLog('views')
log.setLevel(logging.DEBUG)

# Set default timeout so requests don't hang for too long 
# and create spinning processes on gateway server.
socket.setdefaulttimeout(8.0)

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
        return HttpResponse('ERROR: %s' % cgi.escape(str(e)))
    
    all_configs = parsed_xml.getElementsByTagName('Configuration')
    for c in all_configs:
        # Extract device and config data from the xml.
        device_id = c.getAttribute('assignToDeviceId').strip()
        config_title = c.getElementsByTagName('Name')[0].firstChild.data.strip()
        config_version = c.getElementsByTagName('Version')[0].firstChild.data.strip()
        
        # Remove the assignToDeviceId attribute before storing config.
        c.removeAttribute('assignToDeviceId')
        config_xml = c.toxml()
        
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
        try:
            # Find existing config - Version is Unique!
            device = Device.objects.get(device_id=device_id)
        except Device.DoesNotExist:
            device = Device(device_id=device_id)
        
        device.config = config
        device.last_updated = datetime.now()
        device.save()
    
    return HttpResponse('Success!')



# External Phone Services for remote phone reprogramming, etc.
def dump_device_config(request, device_id, software_version, config_version):
    device = get_document_or_404(Device, device_id=device_id)
    try:
        config = device.config
        request_success = True
    except:
        # No assigned or default config found - Log this?
        config = None
        request_success = False    
    
    if config:
        # Ping the primary server to record the device's request.
        # Cache the ping and retry later if is internet down.
        try:
            config_url = reverse('dump_device_config', kwargs={
                'device_id':device.device_id,
                'software_version':software_version,
                'config_version':config_version,
            }).lstrip('/')
        
            request_url = os.path.join(settings.MAIN_SERVER_URL, config_url)
            response = urllib2.urlopen(request_url)
            
            # Loop through old requests that failed and were stored.
            for cr in ConfigRequestCache.objects(request_sent=None):
                response = urllib2.urlopen(cr.url)
                cr.request_sent = datetime.now()
                cr.save()
        except:
            # Initial ping failed - save request for later.
            new_cr = ConfigRequestCache(
                url=request_url,
                request_sent=None,
            )
            new_cr.save()
        
        # Display XML Configuration to Phone.
        device.last_config_request = datetime.now()
        device.save()
        parsed_xml = config.get_parsed_xml()
        return HttpResponse(parsed_xml.toprettyxml(), mimetype='application/xml')
    else:
        raise Http404


