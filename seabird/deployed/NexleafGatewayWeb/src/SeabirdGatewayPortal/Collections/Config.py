from datetime import datetime, date, time, timedelta
from random import randint
from xml.dom import minidom

from mongoengine import Document, DateTimeField, DictField,\
    IntField, ListField, SortedListField, StringField, URLField

# As you are creating this collection, make a list of questions to ask Martin.
class NewConfig(Document):
    name = StringField(required=True)
    version = StringField(unique=True, required=True)
    
    # Settings
    deployment_id = StringField(required=True)
    station_id = StringField(required=True)
    upload_url = URLField(verify_exists=False, required=True)
    
    # Choices: cell, logger, wifi
    radio_upload_mode = StringField(required=True)
    
    # All using minutes.
    upload_interval = IntField(required=True)
    logcat_to_db_flush_interval = IntField(required=True)
    log_db_to_file_flush_cycle = IntField(required=True)
        
    # Mongo Field Stored as DateTime Field (the only one it supports).  
    # Property allows us to interact with it like a python "Time" object.
    _reboot_time = DateTimeField(required=True)
    
    @property
    def reboot_time(self):
        '''GET Method for reboot_time property.'''
        return self._reboot_time.time()
    
    @reboot_time.setter
    def reboot_time(self, value):
        '''
            SET Method for reboot_time property.
            -- Assigned value should ALWAYS be a Time object.
        '''
        if isinstance(value, time):
            # Use a dummy date so it can be stored as a DateTime in Mongo.
            self._reboot_time = datetime.combine(date(2011,1,1), value)
        else:
            raise TypeError('Invalid object type assigned to Reboot Time - requires Time Object')
    
    recording_schedules = SortedListField(DictField(), required=False)
    # DICT Includes:
    # -- start_date (Can't be stored as "Date" object - not BSON Compatible)
    # -- end_date "SAME"
    # -- start_time "SAME (Time object)"
    # -- end_time "SAME (Time object)"
    # -- duration_min (computed from start / end times)
    # -- interval_min
    # -- sampling_length_min
        
    
    # Also the "Config Date" in the XML.
    created_date = DateTimeField(required=True)
    
    # TODO: Make an XML property for displaying the xml.
    
    def __unicode__(self):
        return '%s' % self.name
    
    def save(self):
        if not self.id:
            now = datetime.now()
            self.created_date = now
            
            # Create a unique version number using the "now" time.
            # Micro Seconds + Random Number should ensure uniqueness
            # (in case datetime is caching somehow)
            self.version = '%i%i%i%i%i%i%i%i' % \
                (now.year, now.month, now.day,
                 now.hour, now.minute, now.second,
                 now.microsecond, randint(1000, 9999))
            
            # TODO: Ensure uniqueness by performing a query?
        
        # Save object.
        super(NewConfig, self).save()
    


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
    

