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

