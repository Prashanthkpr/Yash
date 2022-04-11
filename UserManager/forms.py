from dataclasses import fields
from django import forms
from UserManager.models import User
from django.core.exceptions import ValidationError
from django.forms.widgets import NumberInput


class UserLoginForm(forms.ModelForm):
        
    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
            self.fields[field].label = self.fields[field].label.title()
            self.fields[field].widget.attrs['placeholder'] = self.fields[field].label.title()
        self.fields['password'].widget.attrs['autocomplete'] = "new-password"
    
    class Meta:
        model = User
        fields = ('email', 'password')
        widgets = {'password': forms.PasswordInput}
        

class UserRegisterForm(forms.ModelForm):
    # date_of_birth = forms.DateField(required=False, widget=NumberInput(attrs={'type':'date'}))
    resume = forms.FileField(
        widget=forms.FileInput(attrs={'accept': '''application/pdf, application/msword'''}),
        required=True,
    )
    password_repeat = forms.CharField(max_length=30, widget=forms.PasswordInput, label='Repeat Password')
    def __init__(self, *args, **kwargs):
        super(UserRegisterForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
            if self.fields[field].label:
                required = ''
                if self.fields[field].required:
                    required = '*'
                self.fields[field].widget.attrs['placeholder'] = self.fields[field].label.title()
                self.fields[field].label = f'{self.fields[field].label.title()}{required}'
        self.fields['password'].widget.attrs['autocomplete'] = "new-password"
        # self.fields['date_of_birth'].widget.attrs.update({'min': '1920-01-01', 'max': '2012-01-01'})
    
    def clean_password_repeat(self):
        password_repeat = self.cleaned_data['password_repeat']
        password = self.cleaned_data['password']
        if password_repeat != password:
            raise ValidationError("Password and Repeat Password must be same")

        # Always return a value to use as the new cleaned data, even if
        # this method didn't change it.
        return password_repeat

    def clean_email(self):
        email = self.cleaned_data['email']
        if not email.endswith('@yash.com'):
            raise ValidationError("Please provide Yash email.")

        # Always return a value to use as the new cleaned data, even if
        # this method didn't change it.
        return email
        
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'employee_code', 
                  'gender', 'resume', 'password', 'password_repeat')
        widgets = {'password': forms.PasswordInput,}   


class UserUpdateForm(forms.ModelForm):
    # date_of_birth = forms.DateField(required=False, widget=NumberInput(attrs={'type':'date'}))
    resume = forms.FileField(
        widget=forms.FileInput(attrs={'accept': '''application/pdf, application/msword'''}),
        required=False,
    )
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'employee_code', 'resume', 'gender', )
    
    def __init__(self, *args, **kwargs):
        super(UserUpdateForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
            if self.fields[field].label:
                required = ''
                if self.fields[field].required:
                    required = '*'
                self.fields[field].widget.attrs['placeholder'] = self.fields[field].label.title()
                self.fields[field].label = f'{self.fields[field].label.title()}{required}'
    def clean_email(self):
        email = self.cleaned_data['email']
        if not email.endswith('@yash.com'):
            raise ValidationError("Please provide Yash email.")

        # Always return a value to use as the new cleaned data, even if
        # this method didn't change it.
        return email


class UserPasswordResetForm(forms.ModelForm):
    password = forms.CharField(max_length=30, widget=forms.PasswordInput, label='Current Password')
    new_password = forms.CharField(max_length=30, widget=forms.PasswordInput, label='New Password')
    repeat_password = forms.CharField(max_length=30, widget=forms.PasswordInput, label='Repeat Password')

    class Meta:
        model = User
        fields = ('password', 'new_password', 'repeat_password')
    
    def clean_repeat_password(self):
        repeat_password = self.cleaned_data['repeat_password']
        new_password = self.cleaned_data['new_password']
        if repeat_password != new_password:
            raise ValidationError("New Password and Repeat Password must be same")

        # Always return a value to use as the new cleaned data, even if
        # this method didn't change it.
        return repeat_password
    
    def __init__(self, *args, **kwargs):
        super(UserPasswordResetForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
            if self.fields[field].label:
                required = ''
                if self.fields[field].required:
                    required = '*'
                self.fields[field].widget.attrs['placeholder'] = self.fields[field].label.title()
                self.fields[field].label = f'{self.fields[field].label.title()}{required}'     