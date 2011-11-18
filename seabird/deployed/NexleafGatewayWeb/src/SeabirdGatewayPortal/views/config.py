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

from SeabirdGatewayPortal.Collections.Config import Config, NewConfig
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
    configs = NewConfig.objects
    return render_to_response('config/all_configs.html', 
        {
            'configs':configs,
            'page_title': 'All Configurations',
        }, context_instance=RequestContext(request))


# View Individual Config
@login_required
def show_config(request, config_id):
    config = get_document_or_404(NewConfig, id=config_id)
    return render_to_response('config/config.html', 
        {
            'config':config,
            'page_title': 'View Configuration: %s' % config.name,
        }, context_instance=RequestContext(request))


# New Config (New Style)
@login_required
def new_config(request):
    RecordingFormSet = formset_factory(RecordingForm, extra=1, can_delete=True)
    if request.method == 'POST':
        config_form = NewConfigForm(request.POST)
        recording_formset = RecordingFormSet(request.POST, prefix='recordingform')
        if config_form.is_valid() and recording_formset.is_valid():
            
            # Initialize collection with config settings - add recordings later.
            new_config = NewConfig(**config_form.cleaned_data)
            
            recording_list = []
            for recording_form in recording_formset.forms:
                # Conditional due to a minor bug in Django (Ticket #11418)
                # -- Deleted "blank" formsets are "valid" but don't have cleaned_data
                # -- So just ignore them when inserting data into mongo.
                if hasattr(recording_form, 'cleaned_data'):
                    # Get value of DELETE from form (and remove it from the dict so it isn't stored)
                    delete_form = recording_form.cleaned_data.pop('DELETE', '')
                    
                    # Don't store empty dicts or deleted recording data!
                    if not delete_form and len(recording_form.cleaned_data.keys()) > 0:
                        recording_list.append(recording_form.cleaned_data)
            new_config.recording_schedules = recording_list
            new_config.save()
            
            messages.success(request, 'You have successfully created the \
            Configuration: %s (Version #: %s).' % (new_config.name, new_config.version))
            return HttpResponseRedirect(reverse('show_config', kwargs={'config_id':new_config.id}))
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



@login_required
def edit_config(request, config_id):
    config = get_document_or_404(NewConfig, id=config_id)
    
    # need at least one recording form on the page to be cloned, etc.
    extra_form = 0
    if len(config.recording_schedules) == 0:
        extra_form = 1
    RecordingFormSet = formset_factory(RecordingForm, extra=extra_form, can_delete=True)
    
    if request.method == 'POST':
        # Include config_id for default validation.
        config_form = NewConfigForm(request.POST, config_id=config.id)
        recording_formset = RecordingFormSet(request.POST, prefix='recordingform')
        
        if config_form.is_valid() and recording_formset.is_valid():
            # Get post data from the config settings form into the collection.
            for field, value in config_form.cleaned_data.items():
                if hasattr(config, field):
                    setattr(config, field, value)
            
            # Get post data from the recording formset (same as new since it's just a list of dicts)
            recording_list = []
            for recording_form in recording_formset.forms:
                # Conditional due to a minor bug in Django (Ticket #11418)
                # -- Deleted "blank" formsets are "valid" but don't have cleaned_data
                # -- So just ignore them when inserting data into mongo.
                if hasattr(recording_form, 'cleaned_data'):
                    # Get value of DELETE from form (and remove it from the dict so it isn't stored)
                    delete_form = recording_form.cleaned_data.pop('DELETE', '')
                    if not delete_form and len(recording_form.cleaned_data.keys()) > 0:
                        recording_list.append(recording_form.cleaned_data)
            config.recording_schedules = recording_list
            config.save()
            
            messages.success(request, 'You have successfully \
            updated the XML Configuration: %s.' % config.name)
            
            return HttpResponseRedirect(reverse('show_config',
                kwargs={'config_id':config.id}))
        else:
            messages.error(request, FORM_ERROR_MSG)
    else:
        # Initialize data using the fields required by the config form.
        # Includes both actual db fields and properties in the Collection.
        fields = NewConfigForm().fields.keys()
        field_dict = dict([(field, getattr(config, field)) for field in fields])
        config_form = NewConfigForm(initial=field_dict)
        
        # Initialize Recording Formset data (easy!)
        recording_formset = RecordingFormSet(initial=config.recording_schedules, prefix='recordingform')
    return render_to_response('config/config_form.html', 
        {
            'page_title': 'Edit Configuration:  %s' % config.name,
            'edit':True,
            'config':config,
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
def edit_old_config(request, config_id):
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

