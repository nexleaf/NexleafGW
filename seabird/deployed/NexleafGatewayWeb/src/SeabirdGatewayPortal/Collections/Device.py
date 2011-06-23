from mongoengine import Document, ReferenceField, StringField

from SeabirdGatewayPortal.Collections.Config import Config

class Device(Document):
    device_id = StringField(unique=True, max_length=128, required=True)
    config = ReferenceField('Config')
    
    def __unicode__(self):
        return '%s' % self.device_id
    


