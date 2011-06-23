from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin

admin.autodiscover()

########################################
# General Site URLs
########################################
urlpatterns = patterns('SeabirdGatewayPortal.views',
    url(r'^$', 'home.home', name='home'),
    url(r'^upload/$', 'upload.upload_data', name='upload_data'),
    url(r'^files/$', 'files.view_incoming', name='view_incoming'),
    url(r'^rsync/$', 'rsync.view_rsync', name='view_rsync'),
    url(r'^cron/$', 'cron.view_cron', name='view_cron'),
    url(r'^cron/toggle/$', 'cron.toggle_default_cron', name='toggle_default_cron'),
    url(r'^cron/set/$', 'cron.set_cron', name='set_cron'),
    
    # Ready only views for Devices and Configs
    # url(r'^devices/$', device.show_all_devices, name='show_all_devices'),
    # url(r'^configs/$', device.show_all_configs, name='show_all_configs'),
    
    
    # API Views
    url(r'^api/configuration/bulk/get/$', 'api.get_bulk_configs', name='get_bulk_configs'),
    
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
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}, name='auth_login'),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'template_name': 'login.html'}, name='auth_logout'),
)


########################################
# Static Media (Development Only)
########################################
if settings.DEV_ENVIRONMENT:
    urlpatterns += patterns('',
        (r'^seabird/static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes': False}),
    )
