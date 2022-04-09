import pytest
from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType

from hotels.models import Hotel


def create_customer_group():
    Group.objects.create(
        name='Пользователь'
    )


def create_admin_group():
    return Group.objects.create(
        name='Администратор'
    )


def create_manager_group():
    return Group.objects.create(
        name='Контент-менеджер'
    )


def create_permission():
    content_type = ContentType.objects.get_for_model(Hotel)
    return Permission.objects.create(
        codename='add_hotels',
        name='Can add hotels',
        content_type=content_type
    )


@pytest.fixture()
def customer(db):
    create_customer_group()
    _customer = User.objects.create_user(
        username='customer',
        password='django',
        email='test@email.com')
    return _customer


@pytest.fixture()
def administrator(db):
    create_customer_group()
    group = create_admin_group()
    _administrator = User.objects.create_user(
        username='administrator', password='django')
    _administrator.groups.clear()
    group.user_set.add(_administrator)
    permission = create_permission()
    _administrator.user_permissions.add(permission)
    return _administrator


@pytest.fixture()
def manager(db):
    create_customer_group()
    group = create_admin_group()
    _manager = User.objects.create_user(
        username='manager', password='django')
    _manager.groups.clear()
    group.user_set.add(_manager)
    permission = create_permission()
    _manager.user_permissions.add(permission)
    return _manager
