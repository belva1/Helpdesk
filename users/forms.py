from django import forms
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from .models import UM


class LoginViewForm(forms.Form):
    """
    Label -> for describing the field,
    Widget -> graphic interface element,
    Attrs -> sets HTML attributes.
    """
    username = forms.CharField(label='Username', widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Please enter username',
        }
    ))

    password = forms.CharField(label='Password', widget=forms.PasswordInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Please enter password',
        }
    ))

    """
    "clean" method is used to validate data entered by the user into a form,
    """
    def clean(self):
        """
        Authenticates the user based on the provided credentials, and throws
        a ValidationError exception if authentication fails (that is, if authenticate
        returned None, meaning the username or password is incorrect).
        """
        if not authenticate(**self.cleaned_data):
            raise ValidationError('Incorrect username or password.')


class RegisterViewForm(forms.Form):
    username = forms.CharField(label='Username', widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Please enter username',
        }
    ))
    first_name = forms.CharField(label='First Name', widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Please enter first name',
        }
    ))
    last_name = forms.CharField(label='Last Name', widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Please enter last name',
        }
    ))
    password = forms.CharField(label='Password', widget=forms.PasswordInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Please enter password',
        }
    ))
    confirm_password = forms.CharField(label='Confirm Password', widget=forms.PasswordInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Please confirm Password',
        }
    ))

    def clean(self):
        username = self.cleaned_data['username']
        try:
            UM.objects.get(username=username)
            self.add_error('username', 'User with this username already exist.')
        except UM.DoesNotExist:
            if self.cleaned_data['password'] != self.cleaned_data['confirm_password']:
                self.add_error('password', 'Password does not match.')
                self.add_error('confirm_password', 'Confirm password does not match.')

    def create_user(self):
        del self.cleaned_data['confirm_password']
        UM.objects.create_user(**self.cleaned_data)
