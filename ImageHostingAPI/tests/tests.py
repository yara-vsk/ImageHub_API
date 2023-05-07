import pytest
from django.urls import reverse
from rest_framework import status



@pytest.mark.django_db
def test_login_superuser(create_superuser, client):
    response = client.login(username='test', password='test')
    assert response == True


@pytest.mark.django_db
def test_all_superuser_image(create_superuser, auth_client):
    response = auth_client.get('api/v1/images/')
    assert response.status_code == 404