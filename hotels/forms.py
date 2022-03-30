from django import forms

from hotels.models import Country, Option, Hotel, Room
from utils.forms import update_fields_widget


class HotelForm(forms.ModelForm):
    class Meta:
        model = Hotel
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        update_fields_widget(self, self.fields, 'form-control')
        self.fields['repaired_recently'].widget.attrs['class'] = 'form-checkbox'


class RoomCreateForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = '__all__'


class RoomUpdateForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        update_fields_widget(self, self.fields, 'form-control')


class HotelFilterForm(forms.Form):
    country = forms.ModelChoiceField(
        label='Направление',
        queryset=Country.objects.all(),
        required=False
    )
    arrival_date = forms.DateTimeField(
        label='Дата заезда',
        widget=forms.DateInput(
            format="%Y-%m-%d", attrs={'type': 'date'}
        ),
        required=False
    )
    departure_date = forms.DateTimeField(
        label='Дата отъезда',
        widget=forms.DateInput(
            format="%Y-%m-%d", attrs={'type': 'date'}
        ),
        required=False
    )
    is_available = forms.BooleanField(
        label='Только доступные варианты',
        widget=forms.CheckboxInput(
            attrs={'type': 'checkbox', 'class': 'form-check-input'}
        ),
        required=False
    )
    min_price = forms.IntegerField(
        min_value=0,
        widget=forms.NumberInput(attrs={'placeholder': 'от', 'class': 'form-control'}),
        required=False
    )
    max_price = forms.IntegerField(
        min_value=0,
        widget=forms.NumberInput(attrs={'placeholder': 'до', 'class': 'form-control'}),
        required=False
    )
    one_star_hotel = forms.BooleanField(
        widget=forms.CheckboxInput(
            attrs={'type': 'checkbox', 'class': 'form-check-input'}
        ),
        required=False
    )
    two_star_hotel = forms.BooleanField(
        widget=forms.CheckboxInput(
            attrs={'type': 'checkbox', 'class': 'form-check-input'}
        ),
        required=False
    )
    three_star_hotel = forms.BooleanField(
        widget=forms.CheckboxInput(
            attrs={'type': 'checkbox', 'class': 'form-check-input'}
        ),
        required=False
    )
    four_star_hotel = forms.BooleanField(
        widget=forms.CheckboxInput(
            attrs={'type': 'checkbox', 'class': 'form-check-input'}
        ),
        required=False
    )
    five_star_hotel = forms.BooleanField(
        widget=forms.CheckboxInput(
            attrs={'type': 'checkbox', 'class': 'form-check-input'}
        ),
        required=False
    )
    options = forms.ModelMultipleChoiceField(
        queryset=Option.objects.all(),
        widget=forms.CheckboxSelectMultiple(
            attrs={'type': 'checkbox', 'class': 'form-check-input'}
        ),
        required=False
    )
    capacity = forms.ChoiceField(
        choices=((1, 1), (2, 2), (3, 3), (4, 4), (5, 5)),
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'form': 'form'})
