from datetime import datetime, date, time
from random import randint
from xml.dom import minidom

from django.template.loader import render_to_string

from mongoengine import BooleanField, DateTimeField, DictField, Document, \
    IntField, ListField, SortedListField, StringField, URLField, ReferenceField

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
DATE_FORMAT = '%Y-%m-%d'
TIME_FORMAT = '%H:%M:%S'

# As you are creating this collection, make a list of questions to ask Martin.
class Config(Document):
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
    
    
    # Each Recording Schedule DICT Includes:
    # -- start_date (Can't be stored as "Date" object - not BSON Compatible)
    # -- end_date "SAME"
    # -- start_time "SAME (Time object)"
    # -- end_time "SAME (Time object)"
    # -- duration_min (computed from start / end times)
    # -- interval_min
    # -- sampling_length_min
    
    # Also uses property so that python objects can be manually encoded and decoded
    # -- DateTime and Time objects aren't BSON Compatible, so can't be easily stored as DictField.
    _recording_schedules = SortedListField(DictField(), required=False)
    
    @property
    def recording_schedules(self):
        '''GET Method for _recording_schedules.'''
        recording_list = []
        for recording_dict in self._recording_schedules:
            if recording_dict.keys() > 0:
                # Convert Date and Time objects string representation back into objects
                # Cast to string before attempting conversion as strptime gets confused about object, it seems (errors).
                recording_dict['start_date'] = datetime.strptime(str(recording_dict['start_date']), DATE_FORMAT).date()
                recording_dict['end_date'] = datetime.strptime(str(recording_dict['end_date']), DATE_FORMAT).date()
            
                recording_dict['start_time'] = datetime.strptime(str(recording_dict['start_time']), TIME_FORMAT).time()
                recording_dict['end_time'] = datetime.strptime(str(recording_dict['end_time']), TIME_FORMAT).time()
                recording_list.append(recording_dict)
        
        return recording_list
    
    
    @recording_schedules.setter
    def recording_schedules(self, value):
        '''
            SET Method for recording_schedules
            -- converts DateTime and Time objects into items that can be readily stored.
            -- takes inputs of a list of dicts OR just a dict (which is appended to existing list).
        '''
        def convert_dict(in_dict):
            # Convert all dates and times into string representations for easy mongo storage.
            for k, v in in_dict.iteritems():
                if isinstance(v, date):
                    in_dict[k] = date.strftime(v, DATE_FORMAT)
                elif isinstance(v, time):
                    in_dict[k] = time.strftime(v, TIME_FORMAT)
            return in_dict
        
        if isinstance(value, list):
            for recording_dict in value:
                recording_dict = convert_dict(recording_dict)
            self._recording_schedules = value
        elif isinstance(value, dict):
            # Allow user to "append" a dict by assigning it to recording_schedules instead of
            # assigning a list.
            value = convert_dict(value)
            self._recording_schedules.append(value)
        else:
            raise TypeError('Invalid object type assigned to Recording Schedules - Must be List or Dict')
    
    
    # Also the "Config Date" in the XML.
    created_date = DateTimeField(required=True)
    
    # Default Config
    default_config = BooleanField(default=False, required=True)
    
    meta = {
        'ordering': ['name']
    }
    
    # XML Property for converting object into a formatted configuration
    @property
    def xml(self):
        return render_to_string('config/config_xml.html', {'config':self})
    
    
    def get_devices(self):
        """Returns all the devices that use this config"""
        
        # Has to be here - causes circular import at the top of file.
        from SeabirdGatewayPortal.Collections.Device import Device
        devices = Device.objects(config=self)
        return devices
    
    
    def __unicode__(self):
        return '%s' % self.name
    
    def save(self):
        now = datetime.now()
        if not self.id:
            self.created_date = now
        
        # Version Number updated EACH TIME the config is edited (not just on creation).
        # Create a unique version number using the "now" time.
        # Micro Seconds + Random Number should ensure uniqueness
        # (in case datetime is caching somehow)
        self.version = '%i%i%i%i%i%i%06i%i' % \
            (now.year, now.month, now.day,
             now.hour, now.minute, now.second,
             now.microsecond, randint(1000, 9999))
        
        # TODO: Ensure uniqueness by performing a query?
        
        # Save object.
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
    




class BaseDeviceConfigRequest(Document):
    """ The Base Class for Individual and Bulk DeviceConfig Requests """
    # Whether a config was successfully displayed to the device.
    request_success = BooleanField(default=False, required=True)
    
    # Can be used to filter internal vs gateway vs phone requests
    request_referrer = StringField(required=False)
    request_remote_addr = StringField(required=False)
    request_remote_host = StringField(required=False)
    request_user_agent = StringField(required=False)
    
    # Timestamp of the request
    request_date = DateTimeField(required=True)
    
    meta = {
        'ordering': ['-request_date']
    }
    
    def save(self, request=None):
        # Only perform during object "creation".
        if not self.id:
            self.request_date = datetime.now()
            if request:
                # Grab Request Header info
                self.request_referrer=request.META.get('HTTP_REFERER', None)
                self.request_remote_addr=request.META.get('REMOTE_ADDR', None)
                self.request_remote_host=request.META.get('REMOTE_HOST', None)
                self.request_user_agent=request.META.get('HTTP_USER_AGENT', None)
        
        super(BaseDeviceConfigRequest, self).save()


# Tracking for when devices request their configurations.
class DeviceConfigRequest(BaseDeviceConfigRequest):
    """ Individual DeviceConfig Requests """
    device = ReferenceField('Device')
    software_version = StringField(required=False) # Software version on the device
    current_config_version = StringField(required=False) # Config version currently on the device
    served_config = ReferenceField('Config', required=False)  # New configuration that is served to device.
    
    meta = {
        'ordering': ['-request_date']
    }
    
    def __unicode__(self):
        return '%s: %s' % (self.device, self.request_date)
    
