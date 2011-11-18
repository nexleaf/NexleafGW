from xml.dom import minidom

from django import forms

from SeabirdGatewayPortal.Collections.Config import NewConfig
from SeabirdGatewayPortal.Collections.Device import Device

# Most basic Device Data form.
class DeviceForm(forms.Form):
    device_name = forms.CharField(max_length=128, required=False, label='Device Name')
    config = forms.ChoiceField(label='XML Configuration')
    
    def __init__(self, *args, **kwargs):
        super(DeviceForm, self).__init__(*args, **kwargs)
        self.fields['config'].choices = [ (c.id, c.name) for c in NewConfig.objects]
    
    def clean_config(self):
        # ChoiceField just returns the ID of the Config.  Return the actual Object.
        config_id = self.cleaned_data['config']
        try:
            config = NewConfig.objects.get(id=config_id)
            self.cleaned_data['config'] = config
            return config
        except:
            raise forms.ValidationError("Invalid XML Configuration Selected.")
            return config_id


# device_id is only "editable" during creation of Devices, hence the subclassed form.
class NewDeviceForm(DeviceForm):
    device_id = forms.CharField(max_length=128, label='Device ID')
    
    def __init__(self, *args, **kwargs):
        super(NewDeviceForm, self).__init__(*args, **kwargs)
        
        # Make sure device_id comes first in any auto rendering.
        device_id_key = self.fields.keyOrder.pop(-1)
        self.fields.keyOrder.insert(0, device_id_key)
    
    # Enforce uniqueness of device id.
    def clean_device_id(self):
        device_id = self.cleaned_data['device_id']
        
        # New Device (NO editing of device_id, so don't have to exclude "self.id")
        if Device.objects(device_id=device_id).count() > 0:
            raise forms.ValidationError("A Device with that Device ID \
            Already Exists. Please select a different one.")
        return device_id

