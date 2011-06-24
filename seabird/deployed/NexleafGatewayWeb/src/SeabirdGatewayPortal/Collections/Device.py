from datetime import datetime

from mongoengine import Document, DateTimeField, ReferenceField, StringField

from SeabirdGatewayPortal.Collections.Config import Config

class Device(Document):
    device_id = StringField(unique=True, max_length=128, required=True)
    config = ReferenceField('Config')
    
    # Last updated from a bulk update.
    last_updated = DateTimeField(required=True)
    meta = {
        'ordering': ['device_id']
    }
    
    def __unicode__(self):
        return '%s' % self.device_id
    
    
    def save(self):
        # Update last_updated any time this is saved
        # Only Current Update Path: Via Bulk Updates
        self.last_updated = datetime.now()
        super(Device, self).save()
    


