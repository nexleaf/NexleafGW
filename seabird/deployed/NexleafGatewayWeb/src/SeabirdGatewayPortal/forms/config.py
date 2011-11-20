from datetime import datetime, date, time, timedelta
from xml.dom import minidom

from django import forms
from django.forms.extras.widgets import SelectDateWidget

from SeabirdGatewayPortal.Collections.Config import Config

RADIO_UPLOAD_CHOICES = (
    ('', "---"),
    ("cell", "cell"),
    ("logger", "logger"),
    ("wifi", "wifi"),
)

# Both of these combine to form a complete configuration.
class ConfigForm(forms.Form):
    # Version and Date are computed automatically while saving configuration.
    name = forms.CharField(label='Config Name')
    
    # Settings:
    deployment_id = forms.CharField(label='Deployment ID', initial="Tern_Island")
    station_id = forms.CharField(label='Station ID', initial="WAM")
    
    upload_url = forms.URLField(label='Upload URL', help_text="Must begin with: http://", initial="http://131.179.144.62/seabird/upload/")
    
    radio_upload_mode = forms.ChoiceField(label='Radio Upload Mode', choices=RADIO_UPLOAD_CHOICES, initial="wifi")
    upload_interval = forms.IntegerField(required=True, min_value=0,
        label="Upload Interval", help_text="In Minutes", initial=5)
    
    logcat_to_db_flush_interval = forms.IntegerField(required=True, min_value=0,
        label="Logcat To Db Flush Interval", help_text="In Minutes", initial=5)
    log_db_to_file_flush_cycle = forms.IntegerField(required=True, min_value=0,
        label="Log Db To File Flush Cycle", help_text="In Minutes", initial=3)
    
    reboot_time = forms.TimeField(required=True, widget=forms.TimeInput(format="%H:%M"), 
        label='Reboot Time', help_text="HH:MM using a 24hr clock.", initial="14:00")
    
    default_config = forms.BooleanField(required=False, label='Default Config',
        help_text='Only one config can be the default.')
    
    def __init__(self, *args, **kwargs):
        # Used to determine if editing or creating a config
        self.config_id = kwargs.pop('config_id', None)
        
        # Call standard init.
        super(ConfigForm, self).__init__(*args, **kwargs)
        
        # Make fields readonly for Tern Island Deployment.
        readonly_fields = ['deployment_id', 'station_id', 'upload_url',
            'radio_upload_mode', 'upload_interval', 'logcat_to_db_flush_interval',
            'log_db_to_file_flush_cycle', 'reboot_time']
        
        # Select drop down doesn't work as readonly - force to be TextInput
        self.fields['radio_upload_mode'].widget = forms.TextInput()
        
        for field_name in readonly_fields:
            self.fields[field_name].widget.attrs['readonly'] = "readonly"
            self.fields[field_name].widget.attrs['class'] = "readonly_field"
    
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
        start_date = self.cleaned_data.get('start_date', None)
        end_date = self.cleaned_data.get('end_date', None)
        
        start_time = self.cleaned_data.get('start_time', None)
        end_time = self.cleaned_data.get('end_time', None)
        
        if start_date and end_date:
            # Make sure end date is after start date.
            if start_date > end_date:
                raise forms.ValidationError("Start date must be before or equal to end date.")
        
        # If start time is 00:00:00 just an "if start_time" check will fail.  Be explicit!
        # https://code.djangoproject.com/changeset/3563  / https://code.djangoproject.com/ticket/2528
        if start_time != '' and start_time != None and end_time != '' and end_time != None:
            
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



