from django import forms
from .models import Alert


class AlertForm(forms.ModelForm):
    class Meta:
        model = Alert
        fields = ['type', 'description']
        widgets = {
            'type': forms.Select(attrs={'class': 'input'}),
            'description': forms.Textarea(attrs={'class': 'textarea', 'rows': 4}),
        }

    def clean_description(self):
        description = self.cleaned_data.get('description')
        if not description or len(description.strip()) == 0:
            raise forms.ValidationError('Description is required.')
        if len(description) > 500:
            raise forms.ValidationError('Description must be less than 500 characters.')
        return description
