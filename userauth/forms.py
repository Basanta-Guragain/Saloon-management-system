from django import forms
from .models import Customer,Booking

class Customerform(forms.ModelForm):
    class Meta:
        model=Customer
        fields=['name','email','password']
    def clean_password(self):
        password = self.cleaned_data.get('password')
         
        return password

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['name','email','phone_number', 'date', 'time', 'services','additional_services']

