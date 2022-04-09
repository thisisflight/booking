import pytest
from django.contrib.auth.models import Group, User


def create_customer_group():
    Group.objects.create(
        name='Пользователь'
    )


@pytest.fixture()
def customer(db):
    create_customer_group()
    _customer = User.objects.create_user(
        username='customer',
        password='django',
        email='test@email.com')
    return _customer
