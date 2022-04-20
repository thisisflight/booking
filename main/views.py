from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView

from hotels.forms import HotelFilterForm
from hotels.models import Country, Hotel, Review
from utils.form_dates import reconfigure_form_dates


class MainPage(TemplateView):
    template_name = 'index.html'

    def get(self, request, *args, **kwargs):
        self.request.GET._mutable = True
        arrival_date, departure_date = (
            reconfigure_form_dates(request.GET, self.request.GET.get('arrival_date'),
                                   self.request.GET.get('departure_date'))
        )
        self.request.session['arrival_date'] = arrival_date
        self.request.session['departure_date'] = departure_date
        capacity = request.GET.get('capacity')
        link = reverse_lazy('hotels:hotels-list')
        search = True if request.GET.get('search') == '1' else False
        if search:
            if arrival_date and departure_date and capacity:
                return HttpResponseRedirect(f"{link}?arrival_date={arrival_date}"
                                            f"&departure_date={departure_date}"
                                            f"&capacity={capacity}")
            elif arrival_date and departure_date:
                return HttpResponseRedirect(f"{link}?arrival_date={arrival_date}"
                                            f"&departure_date={departure_date}")
            elif arrival_date and capacity:
                return HttpResponseRedirect(f"{link}?arrival_date={arrival_date}"
                                            f"&capacity={capacity}")
            elif capacity:
                return HttpResponseRedirect(f"{link}?capacity={capacity}")
            elif arrival_date:
                return HttpResponseRedirect(f"{link}?arrival_date={arrival_date}")
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        countries = Country.objects.with_cheapest_price().only('name', 'photo')
        hotels = Hotel.objects.select_related('city').prefetch_related('reservations__reviews')
        hotels = hotels.with_cheapest_price_and_average_rate()
        hotels = hotels.only('name', 'city', 'photo').order_by('min_price')[:3]
        reviews = Review.objects.select_related('reservation__user__profile')
        reviews = reviews.only(
            'updated',
            'text',
            'reservation__user__first_name',
            'reservation__user__last_name'
        ).order_by('-pk')[:3]
        context['flag'] = True
        context['main'] = True
        context['countries'] = countries
        context['hotels'] = hotels
        context['reviews'] = reviews
        context['form'] = HotelFilterForm()
        return context
