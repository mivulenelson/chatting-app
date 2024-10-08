from django import forms
from django.core.exceptions import ValidationError
from .models import CustomUser
from django.contrib.auth.forms import ReadOnlyPasswordHashField
import re


class CustomUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ("username", "email")

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords do not match.")
        return password2

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not re.match(r'^[a-zA-Z0-9._%+-]+@gmail\.com$', email):
            raise forms.ValidationError("Email must be a valid Gmail address.")
        return email

    def save(self, commit=False):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password2"])
        if commit:
            user.save()
        return user


class CustomUserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = CustomUser
        fields = ("email", "username")
