from django.views.generic import TemplateView

from hotels.models import Country, Hotel, Review


class MainPage(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        countries = Country.objects.with_cheapest_price()
        hotels = Hotel.objects.select_related('city').with_cheapest_price()
        reviews = Review.objects.select_related('user', 'hotel').all().order_by('-pk')[:3]
        context['flag'] = True
        context['main'] = True
        context['countries'] = countries
        context['hotels'] = hotels
        context['reviews'] = reviews
        return context
