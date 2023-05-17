import os
import shutil

import pytest
from ImageHostingAPI.settings import BASE_DIR
from image.models import Image
from tests.conftest import file_path


@pytest.mark.django_db
def test_login_superuser(create_superuser, client):
    response = client.login(username='test', password='test')
    assert response == True


@pytest.mark.django_db
def test_create_superuser_image(create_superuser, auth_client):
    with open(file_path, 'rb') as file:
        response = auth_client.post('/api/v1/images/', data={'file': file})
    assert response.status_code == 201


@pytest.mark.django_db
def test_get_all_superuser_images(create_superuser, auth_client):
    with open(file_path, 'rb') as file:
        auth_client.post('/api/v1/images/', data={'file': file})
    response = auth_client.get('/api/v1/images/')
    data = response.data
    image = Image.objects.filter(id=1).first()
    image_path = os.path.join(BASE_DIR, 'media', image.image.name)
    assert response.status_code == 200
    assert len(data) == 1
    assert data
    assert os.path.isfile(image_path) == True
    assert data[0]['id'] == 1
    assert data[0]['links']['link_originally_image'] == 'http://testserver/media/'+image.image.name
    assert data[0]['links']['thumbnail_200_link'] == 'http://testserver/media/' + image.image.name + '?height=200'
    assert data[0]['links']['thumbnail_400_link'] == 'http://testserver/media/' + image.image.name + '?height=400'


@pytest.mark.django_db
def test_get_superuser_image(create_superuser, auth_client, create_superuser_image):
    response = auth_client.get('/media/'+create_superuser_image.image.name)
    assert response.status_code == 200


@pytest.mark.django_db
def test_get_superuser_thumbnail_200(create_superuser, auth_client, create_superuser_image):
    response = auth_client.get('http://testserver/media/' + create_superuser_image.image.name + '?height=200')
    assert response.status_code == 200


@pytest.mark.django_db
def test_get_superuser_thumbnail_400(create_superuser, auth_client, create_superuser_image):
    response = auth_client.get('http://testserver/media/'+create_superuser_image.image.name + '?height=400')
    assert response.status_code == 200


@pytest.mark.django_db
def test_get_no_auth_image(auth_client, create_superuser_image):
    response1 = auth_client.get('http://testserver/media/' + create_superuser_image.image.name)
    auth_client.logout()
    response2 = auth_client.get('http://testserver/media/'+create_superuser_image.image.name)
    assert response1.status_code == 200
    assert response2.status_code == 403


def test_delete_all_images():
    image_path = os.path.join(BASE_DIR, 'media', 'user_1')
    shutil.rmtree(image_path)


