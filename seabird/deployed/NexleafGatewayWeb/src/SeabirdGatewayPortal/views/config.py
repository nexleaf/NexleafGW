import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.forms.formsets import formset_factory
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext

from mongoengine import connect
from mongoengine.django.shortcuts import get_document_or_404

from SeabirdGatewayPortal.Collections.Config import Config
from SeabirdGatewayPortal.Collections.Device import Device
from SeabirdGatewayPortal.common.constants import FORM_ERROR_MSG
from SeabirdGatewayPortal.forms.config import ConfigForm, NewConfigForm, RecordingForm
from SeabirdGatewayPortal.utils.Logger import getLog

# Connect to MongoDB - Gateway.
connect('SeabirdGWDB')

log = getLog('views')
log.setLevel(logging.DEBUG)

# Show All Configs
@login_required
def show_all_configs(request):
    configs = Config.objects
    return render_to_response('config/all_configs.html', 
        {
            'configs':configs,
            'page_title': 'All Configurations',
        }, context_instance=RequestContext(request))


# View Individual Config
@login_required
def show_config(request, config_id):
    config = get_document_or_404(Config, id=config_id)
    return render_to_response('config/config.html', 
        {
            'config':config,
            'page_title': 'View Configuration: %s' % config.title,
        }, context_instance=RequestContext(request))


# New Config (New Style)
@login_required
def new_config(request):
    RecordingFormSet = formset_factory(RecordingForm, extra=1, can_delete=True)
    
    if request.method == 'POST':
        config_form = NewConfigForm(request.POST)
        recording_formset = RecordingFormSet(request.POST, prefix='recordingform')
        if config_form.is_valid() and recording_formset.is_valid():
            # TODO: Save New Config.
            messages.success(request, 'You have successfully \
            created the Configuration: %s.' % 'test')
            return HttpResponseRedirect(reverse('show_all_configs'))
            
            # new_config = Config(**form.cleaned_data)
            # new_config.save()
            # return HttpResponseRedirect(reverse('show_config',
            #                 kwargs={'config_id':new_config.id}))
        else:
            messages.error(request, FORM_ERROR_MSG)
    else:
        config_form = NewConfigForm()
        recording_formset = RecordingFormSet(prefix='recordingform')
    
    return render_to_response('config/config_form.html', 
        {
            'page_title': 'Add New Configuration',
            'edit':False,
            'config_form':config_form,
            'recording_formset':recording_formset,
        }, context_instance=RequestContext(request))


# New Config (using old style form / collection).
@login_required
def new_old_config(request):
    if request.method == 'POST':
        form = ConfigForm(request.POST)
        if form.is_valid():
            new_config = Config(**form.cleaned_data)
            new_config.save()
            messages.success(request, 'You have successfully \
            created the XML Configuration: %s.' % new_config.title)
            return HttpResponseRedirect(reverse('show_config',
                kwargs={'config_id':new_config.id}))
        else:
            messages.error(request, FORM_ERROR_MSG)
    else:
        form = ConfigForm()
    return render_to_response('config/config_form.html', 
        {
            'page_title': 'Add New Configuration',
            'edit':False,
            'form':form,
        }, context_instance=RequestContext(request))


# Edit Existing Config
@login_required
def edit_config(request, config_id):
    config = get_document_or_404(Config, id=config_id)
    if request.method == 'POST':
        # Include pk for uniqueness validation.
        form = ConfigForm(request.POST, config_id=config.id)
        if form.is_valid():
            # Get post data from the form into the collection.
            for field, value in form.cleaned_data.items():
                if field in config._fields.keys():
                    config[field] = value
            config.save()
            messages.success(request, 'You have successfully \
            updated the XML Configuration: %s.' % config.title)
            return HttpResponseRedirect(reverse('show_config',
                kwargs={'config_id':config.id}))
        else:
            messages.error(request, FORM_ERROR_MSG)
    else:
        # Initialize the form
        fields = config._fields.keys()
        field_dict = dict([(name, config[name]) for name in fields])
        form = ConfigForm(initial=field_dict)
    return render_to_response('config/config_form.html', 
        {
            'page_title': 'Edit Configuration: %s' % config.title,
            'edit':True,
            'config':config,
            'form':form,
        }, context_instance=RequestContext(request))

