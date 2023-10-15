from django import forms
from .models import Comment
# from django.contrib.auth import authenticate
# from django.core.exceptions import ValidationError
# from .models import UM

FORM_CONTROL_ATTRS = {
    'class': 'form-control',
}


class CommentUpdateForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']

    text = forms.CharField(label='Text', widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Please enter text',
        }
    ))


class CommentCreateForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']

    text = forms.CharField(label='Text', widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Please enter text',
        }
    ))