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
    int_part = int(value)
    float_part = value - int_part
    float_part = float_part * 10 if float_part else 0
    return '.'.join([str(int_part), str(float_part)])


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
def get_rate(reservation, user):
    if reservation.user == user and reservation.rate > 0:
        return reservation.rate
    return '--'
