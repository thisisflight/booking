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
