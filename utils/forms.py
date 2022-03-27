def update_fields_widget(form, fields, css_class):
    for field in fields:
        form.fields[field].widget.attrs.update({'class': css_class})


def set_required_false_to_fields(form, fields):
    for field in fields:
        form.fields[field].required = False
