from django import forms
from django.forms import ModelForm, ValidationError
from django.contrib.auth import authenticate # Necesario para autenticar
from .models import *


class CallLoginForm(ModelForm):
    password = forms.CharField(
        required=True,
        max_length=32,
        min_length=1,
        widget=forms.PasswordInput
    )

    def clean(self):
        cd = self.cleaned_data

        password = cd.get('password')

        call_count = Call.objects.filter(password=password).count()

        if call_count != 1:
            raise forms.ValidationError("This account is already doing an exam.")
        #else:
         #   raise forms.ValidationError("We don't have any account related to that email.")
