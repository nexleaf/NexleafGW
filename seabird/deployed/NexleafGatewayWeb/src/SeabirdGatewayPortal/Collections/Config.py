from datetime import datetime

from mongoengine import Document, DateTimeField, StringField

class Config(Document):
    title = StringField(required=True)
    xml = StringField(required=True)
    version = StringField(unique=True, required=True)
    created_date = DateTimeField(required=True)
    meta = {
        'ordering': ['title']
    }
    
    def get_devices(self):
        """Returns all the devices that use this config"""
        
        # Has to be here - causes circular import at the top of file.
        from Collections.Device import Device
        devices = Device.objects(config=self)
        return devices
    
    
    def __unicode__(self):
        return '%s' % self.title
    
    
    def save(self):
        if not self.id:
            self.created_date = datetime.now()
        super(Config, self).save()
    

