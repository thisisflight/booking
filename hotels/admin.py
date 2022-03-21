from django.contrib import admin
from django.db.models import Prefetch
from django.utils.safestring import mark_safe

from .models import (Country, City, Hotel, Option,
                     Room, Review, Reservation)


class ReservationInline(admin.StackedInline):
    model = Reservation
    extra = 0

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "room":
            hotel_id = request.resolver_match.kwargs.get('object_id')
            kwargs["queryset"] = Room.objects.select_related('hotel').filter(hotel_id=hotel_id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('user', 'hotel', 'room')
        return queryset


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
    inlines = [ReservationInline]


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
