from django import forms
from .models import Event

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'description', 'contact', 'start_date', 'end_date', 
                 'number', 'nameprefix', 'comment']
        
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'end_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'description': forms.Textarea(attrs={'rows': 3}),
            'comment': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nameprefix'].help_text = "Die generierten Usernamen werden aus diesem Prefix und einer Nummer bestehen"
        self.fields['contact'].help_text ="Geben Sie die Email-Adresse für einen Ansprechpartner für diese Veranstaltung an"