from django.contrib import admin
from .models import (Country, City, Hotel, Option,
                     Room, Review, Reservation)
from django.utils.safestring import mark_safe


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    def show_country_photo(self, obj):
        return mark_safe(f"<img src='{obj.photo.url}' "
                         f"style='max-width: 150px; max-height: 150px;'")

    show_country_photo.short_description = 'Фотопревью'
    list_display = ['name', 'show_country_photo']


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['name', 'country']
    list_select_related = ['country']


@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    def show_hotel_photo(self, obj):
        return mark_safe(f"<img src='{obj.photo.url}' "
                         f"style='max-width: 150px; max-height: 150px;'")

    show_hotel_photo.short_description = 'Фотопревью'
    list_display = ['name', 'show_hotel_photo', 'city',
                    'category', 'repaired_recently']
    list_select_related = ['country', 'city']


@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    pass


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    def show_room_photo(self, obj):
        return mark_safe(f"<img src='{obj.photo.url}' "
                         f"style='max-width: 150px; max-height: 150px;'")

    show_room_photo.short_description = 'Фотопревью'
    list_display = ['hotel', 'show_room_photo', 'type', 'price']
    list_select_related = ['hotel']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    pass


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    pass
