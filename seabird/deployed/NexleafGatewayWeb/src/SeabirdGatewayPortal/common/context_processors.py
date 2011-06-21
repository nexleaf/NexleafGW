from django.conf import settings

# Adding MEDIA_URL to the context for static media.
def media_url(request):    
    return {'MEDIA_URL': settings.MEDIA_URL}


