from django import forms
from .models import EventSubscription

class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = EventSubscription
        fields = ('user_name', 'user_email', 'user_phone', 'additional_details')
        widgets = {
            'additional_details': forms.Textarea(attrs={'rows': 4}),
        }