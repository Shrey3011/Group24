from django.forms import ModelForm
from .models import *
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User

class CreateUserForm(UserCreationForm):

    firstname=forms.CharField(max_length=30)
    lastname=forms.CharField(max_length=30)

    class Meta:
        model=User
        fields=['username','firstname','lastname','email','password1','password2']

class CustomerForm(ModelForm):
    class Meta:
        model=Customer
        fields='__all__'
        exclude=['user','email']

    def __init__(self, *args, **kwargs):
        super(CustomerForm, self).__init__(*args, **kwargs)
        self.fields['city'].required = False
        self.fields['state'].required = False
        self.fields['country'].required = False
        self.fields['contact_no'].required = False

class AddvehicleForm(ModelForm):
    class Meta:
        model=Vehicle
        fields='__all__'
        exclude=['owner','tags','status']

class RequestForm(ModelForm):

    start_date = forms.DateField(widget=forms.widgets.DateInput(
        attrs={'type': 'date', 'placeholder': 'yyyy-mm-dd (DOB)', 'class': 'form-control'})
    )

    end_date = forms.DateField(widget=forms.widgets.DateInput(
        attrs={'type': 'date', 'placeholder': 'yyyy-mm-dd (DOB)', 'class': 'form-control'})
    )

    class Meta:
        model=Request_rent
        fields=['start_date','end_date']
        
