from django.contrib.auth.forms import AuthenticationForm
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

    def save(self, commit=True):
        user = super().save(commit=False)
        # Установите значение username как email или phone_number, если оно не указано
        user.username = self.cleaned_data.get('email')
        user.set_password(CustomUser.objects.make_random_password())  # Установите временный пароль
        if commit:
            user.save()
        return user
