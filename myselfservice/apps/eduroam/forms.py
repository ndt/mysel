# forms.py
from django import forms
from .models import EduroamAccount

class EduroamAccountForm(forms.ModelForm):
    class Meta:
        model = EduroamAccount
        fields = ['comment']
        widgets = {
            'comment': forms.TextInput(attrs={'placeholder': 'z.B. Handy, Laptop etc.'})
        }