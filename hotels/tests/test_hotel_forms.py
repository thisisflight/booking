import pytest
from django.test.client import Client

from hotels.forms import RoomFormset

client = Client()


def test_empty_formset_is_not_valid(customer):
    client.force_login(customer)
    form = RoomFormset(data={})
    valid_status = form.is_valid()
    assert valid_status == False
