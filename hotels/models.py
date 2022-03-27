from django.contrib.auth.models import User
from django.core.validators import (MinValueValidator,
                                    MaxValueValidator)
from django.db import models
from django.urls import reverse

from .managers import CustomCountryQuerySet, CustomHotelQuerySet


class Country(models.Model):
    objects = CustomCountryQuerySet.as_manager()

    name = models.CharField(
        max_length=250, verbose_name='Страна'
    )
    photo = models.ImageField(
        upload_to='countries',
        verbose_name='Фото из страны'
    )

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'countries'
        verbose_name = 'Страна'
        verbose_name_plural = 'Страны'


class City(models.Model):
    name = models.CharField(
        max_length=250, verbose_name='Название города'
    )
    country = models.ForeignKey(
        Country, related_name='cities',
        on_delete=models.CASCADE, verbose_name='Страна'
    )

    def __str__(self):
        return f"{self.name}"

    class Meta:
        db_table = 'cities'
        verbose_name = 'Город'
        verbose_name_plural = 'Города'


class Option(models.Model):
    name = models.CharField(
        max_length=250, verbose_name='Название опции'
    )

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'options'
        verbose_name = 'Опция'
        verbose_name_plural = 'Опции'


class Hotel(models.Model):
    objects = CustomHotelQuerySet.as_manager()

    name = models.CharField(
        max_length=250, verbose_name='Название отеля'
    )
    photo = models.ImageField(
        upload_to='hotels',
        verbose_name='Фотография'
    )
    category = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Категория'
    )
    repaired_recently = models.BooleanField(
        default=False, verbose_name='Недавно отремонтирован'
    )
    options = models.ManyToManyField(
        Option, verbose_name='Опции отеля'
    )
    description = models.TextField(
        max_length=2000, verbose_name='Описание отеля'
    )
    country = models.ForeignKey(
        Country, related_name='hotels', on_delete=models.CASCADE,
        verbose_name='Страна'
    )
    city = models.ForeignKey(
        City, related_name='cities', on_delete=models.CASCADE,
        verbose_name='Город'
    )

    def __str__(self):
        return f'{self.name}'

    def get_absolute_url(self):
        return reverse('hotels:hotel-detail', kwargs={'pk': self.pk})

    class Meta:
        db_table = 'hotels'
        verbose_name = 'Отель'
        verbose_name_plural = 'Отели'


class Room(models.Model):
    ROOM_TYPES = (
        ('Комфорт', 'Комфорт'),
        ('Полулюкс', 'Полулюкс'),
        ('Люкс', 'Люкс')
    )
    hotel = models.ForeignKey(
        Hotel, related_name='rooms', on_delete=models.CASCADE,
        verbose_name='Отель'
    )
    type = models.CharField(
        max_length=50, choices=ROOM_TYPES, verbose_name='Тип номера'
    )
    photo = models.ImageField(
        upload_to='rooms', verbose_name='Фотография номера'
    )
    price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name='Цена'
    )
    description = models.TextField(
        max_length=1000, verbose_name='Описание номера'
    )
    capacity = models.PositiveSmallIntegerField(
        default=2,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Вместимость'
    )

    def __str__(self):
        return f'{self.type}'

    class Meta:
        db_table = 'rooms'
        verbose_name = 'Номер'
        verbose_name_plural = 'Номера'


class Reservation(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Гость', related_name='reservations'
    )
    hotel = models.ForeignKey(
        Hotel, on_delete=models.CASCADE,
        verbose_name='Отель', related_name='reservations',
        null=True
    )
    room = models.ForeignKey(
        Room, on_delete=models.CASCADE,
        verbose_name='Номер', related_name='reservations'
    )
    arrival_date = models.DateField(
        verbose_name='Дата приезда'
    )
    departure_date = models.DateField(
        verbose_name='Дата отъезда'
    )

    def __str__(self):
        return f"{self.user.username} {self.arrival_date} - {self.departure_date}"

    class Meta:
        db_table = 'reservations'
        verbose_name = 'Бронь'
        verbose_name_plural = 'Брони'


class Review(models.Model):
    reservation = models.ForeignKey(
        Reservation, on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Бронь',
        null=True
    )
    rate = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Рейтинг'
    )
    text = models.TextField(
        max_length=3000, verbose_name='Текст отзыва'
    )
    created = models.DateTimeField(
        auto_now_add=True, verbose_name='Создан'
    )
    updated = models.DateTimeField(
        auto_now=True, verbose_name='Изменен'
    )

    def __str__(self):
        return str(self.reservation)

    class Meta:
        db_table = 'reviews'
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
