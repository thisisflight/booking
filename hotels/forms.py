from django import forms

from hotels.models import Country, Option, Hotel, Room, Review
from utils.forms import update_fields_widget


class HotelForm(forms.ModelForm):
    class Meta:
        model = Hotel
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        update_fields_widget(self, self.fields, 'form-control')
        self.fields['repaired_recently'].widget.attrs['class'] = 'form-checkbox'


class RoomCreationForm(forms.ModelForm):
    class Meta:
        model = Room
        exclude = ['hotel', 'id', 'capacity']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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


class ReviewForm(forms.ModelForm):

    CHOICES = ((5, 5), (4, 4), (3, 3), (2, 2), (1, 1))

    class Meta:
        model = Review
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['reservation'].widget = forms.HiddenInput()
        self.fields['rate'].widget = forms.Select(choices=self.CHOICES)
