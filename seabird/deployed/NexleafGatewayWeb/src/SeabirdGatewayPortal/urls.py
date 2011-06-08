from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin
admin.autodiscover()

import SeabirdGatewayPortal.views.home as home
import SeabirdGatewayPortal.views.upload as upload
import SeabirdGatewayPortal.views.files as files
import SeabirdGatewayPortal.views.cron as cron
import SeabirdGatewayPortal.views.rsync as rsync

urlpatterns = patterns('',
                       (r'^$', home.home),
                       (r'^upload/$', upload.upload_data),
                       (r'^files/$', files.view_incoming),
                       (r'^rsync/$', rsync.view_rsync),
                       (r'^cron/$', cron.view_cron),
                       (r'^cron/toggle/$', cron.toggle_default_cron),
                       (r'^cron/set/$', cron.set_cron),



                       # !! debug output !!
                       #(r'^debug/$', debug.debug),
                       #(r'^debug/uploads/$', debug.uploads),
                       #(r'^debug/files/(\w*)/$', files.uploadfile),
                       #(r'^debug/metrics_device/$', debug.metrics_device),
                       #(r'^debug/metrics_deployment/$', debug.metrics_deployment),
                       
                       # for admin 
                       (r'^admin/', include(admin.site.urls)),

                       # Data Login/Logout
                       (r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),
                       (r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'template_name': 'login.html'}),
                       )
