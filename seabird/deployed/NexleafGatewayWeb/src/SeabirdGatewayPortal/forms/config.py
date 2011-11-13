from xml.dom import minidom

from django import forms

from SeabirdGatewayPortal.Collections.Config import Config

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
    

