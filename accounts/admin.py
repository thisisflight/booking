from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.forms import BaseInlineFormSet

from .models import Profile


class MyInlineFormset(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queryset = self.queryset.select_related('user')


class ProfileInline(admin.StackedInline):
    model = Profile
    formset = MyInlineFormset
    can_delete = False
    verbose_name = 'Профиль'
    verbose_name_plural = 'Профили'


class CustomUserAdmin(UserAdmin):
    inlines = [ProfileInline]


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
