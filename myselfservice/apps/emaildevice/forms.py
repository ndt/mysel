# forms.py
from django import forms
from .models import EmailDevice

class EmailDeviceForm(forms.ModelForm):
    class Meta:
        model = EmailDevice
        fields = ['comment']
        widgets = {
            'comment': forms.TextInput(attrs={'placeholder': 'z.B. Handy, Laptop etc.'})
        }