from datetime import datetime

from mongoengine import Document, DateTimeField, ReferenceField, StringField

from SeabirdGatewayPortal.Collections.Config import Config, DeviceConfigRequest

class Device(Document):
    device_id = StringField(unique=True, max_length=128, required=True)
    device_name = StringField(max_length=128)
    config = ReferenceField('Config', required=False)
    
    # Last updated from a bulk update.
    last_updated = DateTimeField(required=True)
    
    # Last Config Request From Device
    last_config_request = DateTimeField()
    
    meta = {
        'ordering': ['device_id']
    }
    
    def get_device_config(self):
        """
            Returns the Config object associated with this Device.
            If none is referenced, then returns the default configuration
            Raises exception if no default configuration is found.
        """
        config = self.config
        try:
            # Force evaluation so we can determine that config is NOT None AND 
            # points to an actual object (lazy evaluation in mongoengine hides 
            # invalid DBRef).
            test_config = config.xml
        except:
            try:
                # Use the default config (if it exists).
                config = Config.objects.get(default_config=True)
            except:
                raise Exception('No Default Object Found.')
        return config
    
    
    def get_config_requests(self):
        """
            Get a list of all the configuration requests made by this device.
            Ordered by date.
        """
        config_requests = DeviceConfigRequest.objects(device=self)
        return config_requests
        
    def __unicode__(self):
        if not self.device_name:
            return '%s' % self.device_id
        else:
            return '%s - %s' % (self.device_id, self.device_name)
    

