from django.db import models
from django.db.models import Min, FloatField, IntegerField, Avg
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
