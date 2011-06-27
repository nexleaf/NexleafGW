from datetime import datetime, date, timedelta
from xml.dom import minidom

from mongoengine import Document, DateTimeField, StringField, URLField

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
        from SeabirdGatewayPortal.Collections.Device import Device
        devices = Device.objects(config=self)
        return devices
    
    
    def get_parsed_xml(self, device_id=None):
        """
            Returns parsed xml for config.  If device_id is provided, inserts
            this as an attribute into the main Configuration element
        """
        parsed_xml = minidom.parseString(self.xml)
        if device_id:
            try:
                # In case of malformed xml (no Configuration element)
                config_element = parsed_xml.getElementsByTagName('Configuration')[0]
                config_element.setAttribute('assignToDeviceId', device_id)
            except:
                pass
        return parsed_xml
    
    
    def __unicode__(self):
        return '%s' % self.title
    
    
    def save(self):
        if not self.id:
            self.created_date = datetime.now()
        super(Config, self).save()
    


class ConfigRequestCache(Document):
    """ 
        Cache's Config Requests to be sent to Main Server later.
        Only used when internet connection isn't available during attempts
        to forward configuration requests onto Main Server.
    """
    url = URLField(verify_exists=False, required=True)
    request_sent = DateTimeField(required=False, default=None)
    created_date = DateTimeField(required=True)
    def save(self):
        if not self.id:
            self.created_date = datetime.now()
        super(ConfigRequestCache, self).save()
    

