import logging

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

# Show All Devices
@login_required
def show_all_devices(request):
    devices = Device.objects
    last_successful_update = None
    if devices.count() > 0:
        try:
            last_successful_update = Device.objects.order_by('-last_updated')[0].last_updated
        except:
            pass
    return render_to_response('device/all_devices.html', 
        {
            'devices':devices,
            'last_successful_update':last_successful_update,
            'page_title': 'All Devices',
        }, context_instance=RequestContext(request))


# View Individual Device
@login_required
def show_device(request, device_id=None):
    device = get_document_or_404(Device, device_id=device_id)
    return render_to_response('device/device.html', 
        {
            'device':device,
            'page_title': 'View Device: %s' % device.device_id,
        }, context_instance=RequestContext(request))

