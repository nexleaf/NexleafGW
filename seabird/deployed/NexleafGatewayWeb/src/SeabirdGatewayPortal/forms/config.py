from datetime import datetime, date, time, timedelta
from xml.dom import minidom

from django import forms
from django.forms.extras.widgets import SelectDateWidget

from SeabirdGatewayPortal.Collections.Config import Config

RADIO_UPLOAD_CHOICES = (
    ("cell", "cell"),
    ("logger", "logger"),
    ("wifi", "wifi"),
)

# Both of these combine to form a complete configuration.
class NewConfigForm(forms.Form):
    # Version and Date are computed automatically while saving configuration.
    name = forms.CharField(label='Config Name')
    
    # Settings:
    deployment_id = forms.CharField(label='Deployment ID')
    station_id = forms.CharField(label='Station ID')
    
    upload_url = forms.URLField(label='Upload URL', help_text="Must begin with: http://")
    
    radio_upload_mode = forms.ChoiceField(label='Radio Upload Mode', choices=RADIO_UPLOAD_CHOICES)
    upload_interval = forms.IntegerField(required=True, min_value=0,
        label="Upload Interval", help_text="In Minutes")
    
    logcat_to_db_flush_interval = forms.IntegerField(required=True, min_value=0,
        label="Logcat To Db Flush Interval", help_text="In Minutes")
    log_db_to_file_flush_cycle = forms.IntegerField(required=True, min_value=0,
        label="Log Db To File Flush Cycle", help_text="In Minutes")
    
    reboot_time = forms.TimeField(required=True, widget=forms.TimeInput(format="%H:%M"), 
        label='Reboot Time', help_text="HH:MM using a 24hr clock.")
    
    def clean_reboot_time(self):
        # Convert cleaned Reboot time into a DateTime for use with Mongo DateTime field.
        # Use dummy date.
        reboot_time = self.cleaned_data.get('reboot_time', '')
        if isinstance(reboot_time, time):
            temp_date = date(2011,1,1)
            self.cleaned_data['reboot_time'] = datetime.combine(temp_date, reboot_time)
            reboot_time = self.cleaned_data['reboot_time']
        
        return reboot_time



class RecordingForm(forms.Form):
    '''
        Form allows for multiple recording schedules to be specified
        for a given Configuration.  Used as part of a formset.
    '''
    # Start and end dates of the config (end date is the expiration date essentially).
    start_date = forms.DateField(widget=SelectDateWidget, required=True, label='Schedule Start Date')
    end_date = forms.DateField(widget=SelectDateWidget, required=True, label='Schedule End Date')
    
    # Daily start and stop times for recording.
    start_time = forms.TimeField(required=True, widget=forms.TimeInput(format="%H:%M"), 
        label='Daily Start Time', help_text="HH:MM using a 24hr clock.")
    end_time = forms.TimeField(required=True, widget=forms.TimeInput(format="%H:%M"), 
        label='Daily End Time', help_text="HH:MM using a 24hr clock.")
    
    # Interval and sampling length of recordings.
    # Duration automatically calculated from start / stop time.
    interval_min = forms.IntegerField(required=True, min_value=0, label="Interval", help_text="In Minutes")
    sampling_length_min = forms.IntegerField(required=True, min_value=0, label="Sampling Length", help_text="In Minutes")
        
    def clean(self):
        start_date = self.cleaned_data.get('start_date')
        end_date = self.cleaned_data.get('end_date')
        
        start_time = self.cleaned_data.get('start_time')
        end_time = self.cleaned_data.get('end_time')
        
        if start_date and end_date:
            # Make sure end date is after start date.
            if start_date > end_date:
                raise forms.ValidationError("Start date must be before or equal to end date.")
        
        if start_time and end_time:
            
            # Make sure start time is before end time.  No midnight crossing allowed!
            if start_time >= end_time:
                raise forms.ValidationError("Start time must be before end time.")
            
            # Calculate duration in minutes (difference between start and end times).
            # Convert into datetime and then subtract to get a timedelta object.
            temp_date = date(2011,1,1)
            time_diff = datetime.combine(temp_date, end_time) - \
                datetime.combine(temp_date, start_time)
            
            # Throw away the seconds remainder (integer math) as we don't care about them (minutes is highest resolution).
            self.cleaned_data['duration_min'] = time_diff.seconds / 60
        
        return self.cleaned_data



class ConfigForm(forms.Form):
    title = forms.CharField(label='Title')
    xml = forms.CharField(widget=forms.Textarea(attrs={'class':'xml_textarea'}))
    version = forms.CharField(label='Version', help_text='Must be Unique!')
    default_config = forms.BooleanField(required=False, label='Default Config',
        help_text='Only one config can be the default.')
    
    def __init__(self, *args, **kwargs):
        # Used to determine if editing or creating a config
        self.config_id = kwargs.pop('config_id', None)
        super(ConfigForm, self).__init__(*args, **kwargs)
    
    def clean_version(self):
        version = self.cleaned_data['version']
        error_msg = "A Configuration with that Version Number Already Exists. \
        Please enter a different one."
        if self.config_id:
            # Editing existing device.
            if Config.objects(id__ne=self.config_id, version=version).count() > 0:
                raise forms.ValidationError(error_msg)
        else:
            # New Device
            if Config.objects(version=version).count() > 0:
                raise forms.ValidationError(error_msg)
        return version
    
    
    # Basic XML Validation (does it parse?)
    def clean_xml(self):
        xml = self.cleaned_data['xml']
        try:
            parsed_xml = minidom.parseString(xml)
        except Exception as e:
            raise forms.ValidationError("Invalid XML: %s" % str(e))
        return xml
    
    
    def clean_default_config(self):
        default_config = self.cleaned_data["default_config"]
        if default_config == True:
            params = {"default_config":True}
            if self.config_id:
                # Editing existing device - exclude it.
                params['id__ne'] = self.config_id
            
            if Config.objects(**params).count() > 0:
                raise forms.ValidationError("Invalid Default Selection. \
                Only one xml configuration can be the default at a time.")
        return default_config
    

