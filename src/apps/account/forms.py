from django import forms

from . import models


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField()


class UserCreateForm(forms.ModelForm):
    class Meta:
        model = models.User
        exclude = ('date_joined',)

    def save(self, *args, **kwargs):
        obj = super().save(*args, **kwargs)
        obj.set_password(self.cleaned_data['password'])
        obj.save()
        return obj


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = models.User
        fields = ('first_name', 'last_name', 'email', 'is_active')

class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = models.User
        fields = ('first_name', 'last_name', 'email', 'phonenumber')


class UserPermissionUpdateForm(forms.ModelForm):
    class Meta:
        model = models.User
        fields = ('groups',)
