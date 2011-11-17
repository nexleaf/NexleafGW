from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin

from SeabirdGatewayPortal.views import config
from SeabirdGatewayPortal.views import device

admin.autodiscover()


########################################
# General Site URLs
########################################
urlpatterns = patterns('SeabirdGatewayPortal.views',
    url(r'^$', 'home.home', name='home'),
    url(r'^home/releases/$', 'home.releases', name='releases'),
    url(r'^upload/$', 'upload.upload_data', name='upload_data'),

    url(r'^files/$', 'files.view_incoming_grid', name='view_incoming'),
    url(r'^files/(?P<device_id>\w+)/(?P<viewdate>\d+)$', 'files.view_device_day', name='view_device_day'),
    #url(r'^data/(?P<deviceId>\w+)/(?P<date>\d+)/audio/$', 'files.get_record_audio', name='get_record_audio'),
    url(r'^files/(?P<device_id>\w+)/(?P<viewdate>\d+)/log/$', 'files.get_record_log', name='get_record_log'),

    url(r'^rsync/$', 'rsync.view_rsync', name='view_rsync'),
    url(r'^cron/$', 'cron.view_cron', name='view_cron'),
    url(r'^cron/toggle/$', 'cron.toggle_default_cron', name='toggle_default_cron'),
    url(r'^cron/set/$', 'cron.set_cron', name='set_cron'),
    
    # Devices
    url(r'^devices/$', 'device.show_all_devices', name='show_all_devices'),
    url(r'^devices/(?P<device_id>\w+)/show/$', 'device.show_device', name='show_device'),
    url(r'^devices/new/$', device.new_device, name='new_device'),
    url(r'^devices/(?P<device_id>\w+)/edit/$', device.edit_device, name='edit_device'),
    
    
    # Configs
    url(r'^configs/$', config.show_all_configs, name='show_all_configs'),
    url(r'^configs/(?P<config_id>\w+)/show/$', config.show_config, name='show_config'),
    url(r'^configs/new/$', config.new_config, name='new_config'),
    url(r'^configs/(?P<config_id>\w+)/edit/$', config.edit_config, name='edit_config'),
    
    # API Views
    url(r'^api/configuration/bulk/get/$', 'api.get_bulk_configs', name='get_bulk_configs'),
    
    # TODO: This should start with /api, but leaving it like this for consistency for device.
    # TODO: Fix it later.
    url(r'^configuration/(?P<device_id>\w+)/(?P<software_version>\w+)/(?P<config_version>\w+)/$',
        'api.dump_device_config', name='dump_device_config'),
    
    
    # !! debug output !!
    #(r'^debug/$', debug.debug),
    #(r'^debug/uploads/$', debug.uploads),
    #(r'^debug/files/(\w*)/$', files.uploadfile),
    #(r'^debug/metrics_device/$', debug.metrics_device),
    #(r'^debug/metrics_deployment/$', debug.metrics_deployment),

    # for admin 
    (r'^admin/', include(admin.site.urls)),

)


########################################
# Account Management URLs
########################################
urlpatterns += patterns('',
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'accounts/login.html'}, name='auth_login'),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'template_name': 'accounts/logged_out.html'}, name='auth_logout'),
)


########################################
# Static Media (Development Only)
########################################
if settings.DEV_ENVIRONMENT:
    urlpatterns += patterns('',
        (r'^seabird/static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes': False}),
    )
