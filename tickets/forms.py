from django import forms
from .models import Ticket
# from django.contrib.auth import authenticate
# from django.core.exceptions import ValidationError
# from .models import UM

FORM_CONTROL_ATTRS = {'class': 'form-control'}
PRIORITY_CHOICES = [('', 'Please select priority')] + Ticket.PRIORITY_CHOICES


# When a ticket is created, the status is automatically assigned to active.
class TicketCreateForm(forms.Form):
    priority = forms.ChoiceField(choices=PRIORITY_CHOICES, widget=forms.Select(
        attrs={
            'class': 'form-control',
        }
    ))
    topic = forms.CharField(label='Topic', widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Please enter topic',
        }
    ))
    description = forms.CharField(label='Description', widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Please enter description',
        }
    ))

    def create_ticket(self, user):
        ticket_data = {
            'priority': self.cleaned_data['priority'],
            'topic': self.cleaned_data['topic'],
            'description': self.cleaned_data['description'],
            'status': 'Active',
            'ticket_user': user,
        }
        return Ticket.objects.create(**ticket_data)


# The user can change the text and/or status of the ticket.
class TicketUserUpdateForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['description', 'priority']

    description = forms.CharField(label='Description', required=False, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Please enter description',
        }
    ))
    priority = forms.ChoiceField(choices=PRIORITY_CHOICES, required=False, widget=forms.Select(attrs=FORM_CONTROL_ATTRS))

    def clean(self):
        cleaned_data = super().clean()
        description = cleaned_data.get('description')
        priority = cleaned_data.get('priority')

        if not description and not priority:
            raise forms.ValidationError("To update should be selected at least one value.")

        return cleaned_data


class TicketDeclineForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['decline_reason']

    decline_reason = forms.CharField(required=True, label='Topic', widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Please enter decline reason',
            'id': 'id_decline_reason'
        }
    ))