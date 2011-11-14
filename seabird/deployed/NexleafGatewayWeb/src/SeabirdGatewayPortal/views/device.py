import logging
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext

from mongoengine import connect
from mongoengine.django.shortcuts import get_document_or_404

from SeabirdGatewayPortal.Collections.Config import Config
from SeabirdGatewayPortal.Collections.Device import Device
from SeabirdGatewayPortal.common.constants import FORM_ERROR_MSG
from SeabirdGatewayPortal.forms.device import DeviceForm, NewDeviceForm
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


# New Device
@login_required
def new_device(request):
    if request.method == 'POST':
        form = NewDeviceForm(request.POST)
        if form.is_valid():
            new_device = Device(**form.cleaned_data)
            new_device.last_updated = datetime.now()
            
            new_device.save()
            messages.success(request, 'You have successfully \
            created Device: %s.' % new_device.device_id)
            return HttpResponseRedirect(reverse('show_device',
                kwargs={'device_id':new_device.device_id}))
        else:
            messages.error(request, FORM_ERROR_MSG)
    else:
        form = NewDeviceForm()
    return render_to_response('device/device_form.html', 
        {
            'page_title': 'Add New Device',
            'edit':False,
            'form':form,
        }, context_instance=RequestContext(request))
    


#
# Edit Existing Device
@login_required
def edit_device(request, device_id=None):
    device = get_document_or_404(Device, device_id=device_id)
    if request.method == 'POST':
        # Include pk for uniqueness validation.
        form = DeviceForm(request.POST)
        if form.is_valid():
            # Get post data from the form into the collection.
            for field, value in form.cleaned_data.items():
                if field in device._fields.keys():
                    device[field] = value
            device.save()
            messages.success(request, 'You have successfully \
            updated Device: %s.' % device.device_id)
            return HttpResponseRedirect(reverse('show_device',
                kwargs={'device_id':device.device_id}))
        else:
            messages.error(request, FORM_ERROR_MSG)
    else:
        # Initialize the edit form
        fields = device._fields.keys()
        field_dict = dict([(name, device[name]) for name in fields])
        
        # Fix the reference to the deviceConfig to be the id
        # instead of the obj for choice field initialization.
        if field_dict.has_key('config'):
            if isinstance(field_dict['config'], Config):
                field_dict['config'] = field_dict['config'].id
        form = DeviceForm(initial=field_dict)
    return render_to_response('device/device_form.html', 
        {
            'page_title': 'Edit Device: %s' % device.device_id,
            'edit':True,
            'device':device,
            'form':form,
        }, context_instance=RequestContext(request))
    

