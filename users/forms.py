from django import forms
from users.models import CustomUser

class RegistrationForm(forms.ModelForm):
    phone_number = forms.CharField(max_length=15, required=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'phone_number']