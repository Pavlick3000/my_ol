from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import ValidationError

from users.models import CustomUser
from django import forms

class UserLoginForm (AuthenticationForm):
    class Meta:
        model = CustomUser
        fields = ('phone_number',)

class CustomUserCreationForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone_number']

    # def clean_email(self):
    #     email = self.cleaned_data.get('email')
    #     if email:
    #         print(f"Checking email: {email}")
    #     if get_user_model().objects.filter(email=email).exists():
    #         print(f"Email {email} already exists in database.")  # Дополнительный вывод
    #         raise ValidationError('Пользователь с таким email уже существует.')
    #     return email
    #
    # def clean_phone_number(self):
    #     phone_number = self.cleaned_data.get('phone_number')
    #     if phone_number:
    #         print(f"Checking phone_number: {phone_number}")
    #     if get_user_model().objects.filter(phone_number=phone_number).exists():
    #         raise ValidationError('Пользователь с таким номером телефона уже существует.')
    #     return phone_number

    def save(self, commit=True):
        user = super().save(commit=False)
        # Установите значение username как email или phone_number, если оно не указано
        user.username = self.cleaned_data.get('email')
        user.set_password(CustomUser.objects.make_random_password())  # Установите временный пароль
        if commit:
            user.save()
        return user
