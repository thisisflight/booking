from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Создание ролей посетителей сайта'

    ROLES = (
        'Администратор',
        'Контент-менеджер',
        'Пользователь'
    )

    def handle(self, *args, **options):
        group_objects = (Group(name=role) for role in self.ROLES)
        Group.objects.bulk_create(group_objects)
