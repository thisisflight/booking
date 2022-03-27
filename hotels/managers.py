from django.db import models
from django.db.models import Min, FloatField, IntegerField, Avg, Count
from django.db.models.functions import Coalesce


class CustomCountryQuerySet(models.QuerySet):
    def with_cheapest_price(self):
        return self.annotate(
            min_price=Coalesce(Min('hotels__rooms__price', output_field=IntegerField()), 0)
        ).all().order_by('-pk')[:3]


class CustomHotelQuerySet(models.QuerySet):
    def with_cheapest_price_and_average_rate(self):
        return self.annotate(
            min_price=Min('rooms__price', output_field=IntegerField()),
            avg_rate=Avg('reviews__rate', output_field=FloatField()),
        ).all()

    def with_all_reservations_and_views(self):
        return self.annotate(
            bookings=Count('reservations', output_field=IntegerField()),
            all_reviews=Count('reservations__reviews', output_field=IntegerField(), distinct=True),
        ).all()
