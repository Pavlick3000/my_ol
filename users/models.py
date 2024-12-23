from django.contrib.auth.models import AbstractUser, Group
from django.db import models
#
class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=15, unique=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None  # Проверяем, новый ли пользователь
        super().save(*args, **kwargs)
        if is_new:  # Если пользователь новый
            guest_group, _ = Group.objects.get_or_create(name='Гость')
            self.groups.add(guest_group)