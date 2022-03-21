from django.contrib.auth.models import User, Group
from django.db import models

from hotels.models import Country, City


class Profile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='profile'
    )
    avatar = models.ImageField(
        upload_to='avatars',
        verbose_name='Изображение профиля'
    )
    phone = models.CharField(
        max_length=20,
        verbose_name='Телефон'
    )
    country = models.ForeignKey(
        Country, on_delete=models.SET_NULL, null=True,
        verbose_name='Страна',
        related_name='profiles'
    )
    city = models.ForeignKey(
        City, on_delete=models.SET_NULL, null=True,
        verbose_name='Город',
        related_name='profiles'
    )
    role = models.ForeignKey(
        Group, on_delete=models.CASCADE,
        verbose_name='Роль пользователя',
        related_name='profiles'
    )

    def __str__(self):
        return self.user.username
