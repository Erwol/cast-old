from django import forms
from django.forms import ModelForm, ValidationError
from django.contrib.auth import authenticate # Necesario para autenticar
from .models import *


# http://www.effectivedjango.com/forms.html
class StudentSignUpForm(ModelForm):

    class Meta:
        model = User

        widgets = {
            'password': forms.PasswordInput(),
            'email': forms.EmailInput(),
        }

        fields = ['first_name', 'last_name', 'email', 'passport'] #, 'password']

    # TODO Añadir verificaciones


class StudentLogInForm(forms.Form):
    email = forms.EmailField(required=True)

    password = forms.CharField(
        required=True,
        max_length=32,
        min_length=1,
        widget=forms.PasswordInput
    )

    def clean(self):
        cd = self.cleaned_data

        email = cd.get('email')

        password = cd.get('password')

        user = authenticate(username=email, password=password)

        if user is not None:
            if not user.is_active or not user.is_student:
                raise forms.ValidationError("The password is valid, but the account has not perms to do this!")
            if StudentProfile.objects.get(user=user).already_on_exam:
                # TODO Controlar esto
                raise forms.ValidationError("This account is already doing an exam.")
        else:
            raise forms.ValidationError("We don't have any account related to that email.")

"""""
    def clean_email(self):
        cd = self.cleaned_data
        email = cd.get('email')
        # num_results = StudentProfile.objects.filter(user__email=email).count()
        num_results = User.objects.filter(email=email).count()
        if num_results != 0:
            user = User.objects.get(email=email)
            if not user.is_student:
                raise forms.ValidationError("This is not a student email.")
        return email

    def clean(self):
        cd = self.cleaned_data

        email = cd.get('email')
        password = cd.get('password')


        num_results = StudentProfile.objects.filter(user__password=password, user__email=email).count()

        if num_results != 1:
            raise forms.ValidationError("Password doesn't match.")



user = authenticate(username='john', password='secret')
if user is not None:
    # the password verified for the user
    if user.is_active:
        print("User is valid, active and authenticated")
    else:
        print("The password is valid, but the account has been disabled!")
else:
    # the authentication system was unable to verify the username and password
    print("The username and password were incorrect.")
"""""