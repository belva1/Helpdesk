from django import forms
from .models import Ticket
# from django.contrib.auth import authenticate
# from django.core.exceptions import ValidationError
# from .models import UM

PRIORITY_CHOICES = [('', 'Please select priority')] + Ticket.PRIORITY_CHOICES

STATUS_CHOICES = [('', 'Please select status')] + [
    (status, label) for status, label in Ticket.STATUS_CHOICES if status not in ('Active', 'InRestoration', 'ApproveRestore')
]

FORM_CONTROL_ATTRS = {
    'class': 'form-control',
}


# The user can change the text and/or status of the ticket.
class TicketUserUpdateForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['description', 'priority']

    description = forms.CharField(label='Description', widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Please enter description',
        }
    ))
    priority = forms.ChoiceField(choices=PRIORITY_CHOICES, widget=forms.Select(attrs=FORM_CONTROL_ATTRS))


# The admin can change status of the ticket.
class TicketAdminUpdateForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['status', 'decline_reason', 'reject_reason']

    def __init__(self, *args, **kwargs):
        super(TicketAdminUpdateForm, self).__init__(*args, **kwargs)
        current_status = self.instance.status if self.instance and hasattr(self.instance, 'status') else None
        if current_status == 'InRestoration':
            self.fields['status'].choices = STATUS_CHOICES + [('ApproveRestore', 'ApproveRestore'),]
        else:
            self.fields['status'].choices = STATUS_CHOICES

    status = forms.ChoiceField(choices=STATUS_CHOICES, widget=forms.Select(
        attrs={
            'class': 'form-control',
            'id': 'id_status'
        }
    ))
    decline_reason = forms.CharField(required=False, label='Topic', widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Please enter decline reason',
            'id': 'id_decline_reason'
        }
    ))
    reject_reason = forms.CharField(required=False, label='Topic', widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Please enter reject reason',
            'id': 'id_reject_reason'
        }
    ))


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