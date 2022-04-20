from django import template

from utils.plural_text import plural_form

register = template.Library()


@register.simple_tag
def plural(value, form1, form2, form3):
    return plural_form(value, form1, form2, form3)


@register.simple_tag
def separate_integers_with_dotes(value):
    return '.'.join([str(value // 1000), '000']) if value >= 1000 else value


@register.simple_tag
def separate_floats_with_dotes(value):
    value = round(float(value), 1)
    return str(value).replace(',', '.')


@register.simple_tag
def beautify_phone_view(phone_number):
    if len(phone_number) == 11:
        return '+7 ({}{}{}) {}{}{}-{}{}-{}{}'.format(*list(phone_number)[1:])
    return phone_number


@register.simple_tag
def if_days_difference_gt_0(td):
    days = td.days
    return True if days > 0 else False


@register.simple_tag
def get_rate(hotels_id_dict, hotel_id):
    rate = hotels_id_dict.get(hotel_id)
    return rate if rate else "--"
