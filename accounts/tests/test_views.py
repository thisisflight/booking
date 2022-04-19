from django.test.client import Client
from django.urls import reverse

client_customer = Client()
client_admin = Client()
client_manager = Client()


def test_customer_cant_see_dashboard(customer):
    client_customer.force_login(customer)
    response = client_customer.get(reverse('accounts:dashboard'))
    assert response.status_code == 403


def test_administrator_can_see_dashboard(administrator):
    client_admin.force_login(administrator)
    response = client_admin.get(reverse('accounts:dashboard'))
    assert response.status_code == 200


def test_manager_can_see_dashboard(manager):
    client_manager.force_login(manager)
    response = client_manager.get(reverse('accounts:dashboard'))
    assert response.status_code == 200
