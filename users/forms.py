from django.contrib.auth.forms import AuthenticationForm
from users.models import CustomUser
from django import forms

# class UserLoginForm (AuthenticationForm):
# class UserLoginForm (forms.Form):
#     class Meta:
#         model = CustomUser
#         fields = ('phone_number', 'email')

class UserLoginForm(forms.Form):
    phone_number = forms.CharField(required=False)
    email = forms.EmailField(required=False)

    def clean(self):
        cleaned_data = super().clean()
        phone_number = cleaned_data.get("phone_number")
        email = cleaned_data.get("email")

        if not phone_number and not email:
            raise forms.ValidationError("Either phone number or email must be provided.")

        return cleaned_data

class CustomUserCreationForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone_number']

    def save(self, commit=True):
        user = super().save(commit=False)
        # Установите значение username как email или phone_number, если оно не указано
        user.username = self.cleaned_data.get('email')
        user.set_password(CustomUser.objects.make_random_password())  # Установите временный пароль
        if commit:
            user.save()
        return user
