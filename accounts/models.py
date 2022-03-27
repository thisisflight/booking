from django.conf import settings
from django.contrib.auth.models import User, Group
from django.db import models
from django.urls import reverse

from hotels.models import Country, City


class Profile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='profile'
    )
    avatar = models.ImageField(
        upload_to='avatars',
        verbose_name='Изображение профиля',
        null=True,
        blank=True
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
        Group, on_delete=models.SET_NULL,
        verbose_name='Роль пользователя',
        related_name='profiles',
        null=True
    )

    def __str__(self):
        return self.user.username

    def get_absolute_url(self):
        return reverse('accounts:profile')

    def get_avatar_url(self):
        return self.avatar.url if self.avatar else f"{settings.STATIC_URL}images/reviewer/1.jpg"
