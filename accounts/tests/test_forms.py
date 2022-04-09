import pytest
from accounts.forms import ChangeProfileInfoForm
from django.test.client import Client

client = Client()


def test_profile_form_not_valid_with_existing_email(customer):
    client.force_login(customer)
    form = ChangeProfileInfoForm(
        data={
            'email': 'test@email.com'
        }
    )
    valid_status = form.is_valid()
    assert valid_status == False


def test_profile_form_not_valid_with_existing_username(customer):
    client.force_login(customer)
    form = ChangeProfileInfoForm(
        data={
            'username': 'customer'
        }
    )
    valid_status = form.is_valid()
    assert valid_status == False
