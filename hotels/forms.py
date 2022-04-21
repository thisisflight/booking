from django import forms

from hotels.models import Country, Option, Hotel, Room, Review, Reservation
from utils.errors import CustomErrorList
from utils.forms import update_fields_widget


class HotelForm(forms.ModelForm):
    class Meta:
        model = Hotel
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        update_fields_widget(self, self.fields, 'form-control')
        self.fields['repaired_recently'].widget.attrs['class'] = 'form-checkbox'
        self.fields['category'].widget.attrs.update({'min': 1, 'max': 5})
        self.fields['category'].initial = 5
        self.fields['options'].widget.attrs.update({'style': 'height: 150px;'})


class RoomCreationForm(forms.ModelForm):
    class Meta:
        model = Room
        exclude = ['hotel', 'id', 'capacity']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        kwargs.update({'error_class': CustomErrorList})
        update_fields_widget(self, self.fields, 'form-control')


class BaseRoomCreationFormset(forms.BaseInlineFormSet):
    def get_queryset(self):
        return Room.objects.none()

    def clean(self):
        if any(self.errors):
            return

        all_forms_is_empty = True

        for form in self.forms:
            all_forms_is_empty = all_forms_is_empty and not any(form.cleaned_data)

        if all_forms_is_empty:
            raise forms.ValidationError("Все формы пустые. Заполните данные.")


RoomFormset = forms.inlineformset_factory(
    Hotel, Room, form=RoomCreationForm, formset=BaseRoomCreationFormset, extra=2
)


class HotelFilterForm(forms.Form):
    country = forms.ModelChoiceField(
        label='Направление',
        queryset=Country.objects.all(),
    )
    arrival_date = forms.DateTimeField(
        label='Дата заезда',
        widget=forms.DateInput(
            format="%Y-%m-%d", attrs={'type': 'date'}
        ),
    )
    departure_date = forms.DateTimeField(
        label='Дата отъезда',
        widget=forms.DateInput(
            format="%Y-%m-%d", attrs={'type': 'date'}
        ),
    )
    is_available = forms.BooleanField(
        label='Только доступные варианты',
        widget=forms.CheckboxInput(
            attrs={'type': 'checkbox', 'class': 'form-check-input'}
        ),
    )
    min_price = forms.IntegerField(
        min_value=0,
        widget=forms.NumberInput(attrs={'placeholder': 'от', 'class': 'form-control'}),
    )
    max_price = forms.IntegerField(
        min_value=0,
        widget=forms.NumberInput(attrs={'placeholder': 'до', 'class': 'form-control'}),
    )
    one_star_hotel = forms.BooleanField(
        widget=forms.CheckboxInput(
            attrs={'type': 'checkbox', 'class': 'form-check-input'}
        ),
    )
    two_star_hotel = forms.BooleanField(
        widget=forms.CheckboxInput(
            attrs={'type': 'checkbox', 'class': 'form-check-input'}
        ),
    )
    three_star_hotel = forms.BooleanField(
        widget=forms.CheckboxInput(
            attrs={'type': 'checkbox', 'class': 'form-check-input'}
        ),
    )
    four_star_hotel = forms.BooleanField(
        widget=forms.CheckboxInput(
            attrs={'type': 'checkbox', 'class': 'form-check-input'}
        ),
    )
    five_star_hotel = forms.BooleanField(
        widget=forms.CheckboxInput(
            attrs={'type': 'checkbox', 'class': 'form-check-input'}
        ),
    )
    options = forms.ModelMultipleChoiceField(
        queryset=Option.objects.all(),
        widget=forms.CheckboxSelectMultiple(
            attrs={'type': 'checkbox', 'class': 'form-check-input'}
        ),
    )
    capacity = forms.ChoiceField(
        choices=((1, 1), (2, 2), (3, 3), (4, 4), (5, 5)),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'form': 'form'})
            self.fields[field].required = False


class ReviewForm(forms.ModelForm):

    CHOICES = ((5, 5), (4, 4), (3, 3), (2, 2), (1, 1))

    class Meta:
        model = Review
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['reservation'].widget = forms.HiddenInput()
        self.fields['rate'].widget = forms.Select(choices=self.CHOICES)

    def clean(self):
        cleaned_data = super().clean()
        reservation = cleaned_data.get('reservation')
        user = reservation.user
        hotel = reservation.hotel
        reservations = Reservation.objects.filter(
            hotel=hotel, user=user)
        if Review.objects.filter(
                reservation__in=reservations).exists():
            raise forms.ValidationError(f'Вы уже оставили отзыв на этот отель')
        return cleaned_data


class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['user', 'hotel', 'room', 'arrival_date', 'departure_date']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'].widget = forms.HiddenInput()
        self.fields['hotel'].widget = forms.HiddenInput()
        self.fields['arrival_date'].widget = forms.DateInput(
            format="%Y-%m-%d", attrs={'type': 'hidden'}
        )
        self.fields['departure_date'].widget = forms.DateInput(
            format="%Y-%m-%d", attrs={'type': 'hidden'}
        )
