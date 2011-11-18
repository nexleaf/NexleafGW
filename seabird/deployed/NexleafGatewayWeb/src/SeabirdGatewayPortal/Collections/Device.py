from datetime import datetime

from mongoengine import Document, DateTimeField, ReferenceField, StringField

from SeabirdGatewayPortal.Collections.Config import NewConfig

class Device(Document):
    device_id = StringField(unique=True, max_length=128, required=True)
    device_name = StringField(max_length=128)
    config = ReferenceField('NewConfig', required=True)
    
    # Last updated from a bulk update.
    last_updated = DateTimeField(required=True)
    
    # Last Config Request From Device
    last_config_request = DateTimeField()
    
    meta = {
        'ordering': ['device_id']
    }
    
    def __unicode__(self):
        if not self.device_name:
            return '%s' % self.device_id
        else:
            return '%s - %s' % (self.device_id, self.device_name)
    

