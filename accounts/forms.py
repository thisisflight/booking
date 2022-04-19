from allauth.account.forms import LoginForm
from django import forms
from django.contrib.auth.forms import (UserCreationForm, PasswordChangeForm,
                                       PasswordResetForm, SetPasswordForm)
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.forms.utils import ErrorList

from utils.forms import update_fields_widget, set_required_false_to_fields
from .models import Profile


class CustomUserCreationForm(UserCreationForm):
    email = forms.CharField(
        widget=forms.EmailInput
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        update_fields_widget(self,
                             ('username', 'email', 'password1', 'password2'),
                             'form-control')


class CustomAuthenticationForm(LoginForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        update_fields_widget(self, ('login', 'password'), 'form-control')


class CustomPasswordChangeForm(PasswordChangeForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        update_fields_widget(self,
                             ('old_password', 'new_password1', 'new_password2'),
                             'form-control')


class CustomPasswordResetForm(PasswordResetForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        update_fields_widget(self, ('email',), 'form-control')


class CustomSetPasswordForm(SetPasswordForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        update_fields_widget(self, ('new_password1', 'new_password2',), 'form-control')


class CustomErrorList(ErrorList):
    def __str__(self):
        return self.as_divs()

    def as_divs(self):
        if not self:
            return ''
        return '<div class="errorlist">%s</div>' % ''.join(['<div style="color: red">%s</div>' % e for e in self])


class ChangeProfileInfoForm(forms.ModelForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={'placeholder': 'Введите новое имя пользователя'}
        )
    )
    email = forms.CharField(
        widget=forms.EmailInput(
            attrs={'placeholder': 'Введите новый адрес электронной почты'}),
    )
    first_name = forms.CharField(
        widget=forms.TextInput(
            attrs={'placeholder': 'Введите имя'}
        )
    )
    last_name = forms.CharField(
        widget=forms.TextInput(
            attrs={'placeholder': 'Введите фамилию'}
        )
    )

    class Meta:
        model = Profile
        exclude = ['user']

    def __init__(self, *args, **kwargs):
        kwargs.update({'error_class': CustomErrorList})
        super().__init__(*args, **kwargs)
        update_fields_widget(self, self.fields, 'form-control')
        set_required_false_to_fields(self, self.fields)

    def clean_username(self):
        cleaned_data = super().clean()
        username_to_check = cleaned_data.get('username')
        username_queryset = User.objects.filter(username__exact=username_to_check).exists()
        if username_queryset:
            raise ValidationError('Пользователь с таким именем уже существует')
        return username_to_check

    def clean_email(self):
        cleaned_data = super().clean()
        email_to_check = cleaned_data.get('email')
        email_queryset = User.objects.filter(email__exact=email_to_check).exists()
        if email_queryset:
            raise ValidationError('Пользователь с такой почтой уже существует')
        return email_to_check
