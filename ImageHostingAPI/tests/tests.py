import os
import pytest
from ImageHostingAPI.settings import BASE_DIR
from image.models import Image
from tests.conftest import file_path


@pytest.mark.django_db
def test_login_superuser(create_superuser, client):
    response = client.login(username='test', password='test')
    assert response == True


@pytest.mark.django_db
def test_login_user(create_user, client):
    response = client.login(username=create_user.username, password='test')
    assert create_user.username in ["user_Basic","user_Premium", "user_Enterprise"]
    assert response == True


@pytest.mark.django_db
def test_create_superuser_image(auth_client_super):
    with open(file_path, 'rb') as file:
        response = auth_client_super.post('/api/v1/images/', data={'file': file})
    assert response.status_code == 201


@pytest.mark.django_db
def test_create_user_image(auth_client):
    with open(file_path, 'rb') as file:
        response = auth_client.post('/api/v1/images/', data={'file': file})
    assert response.status_code == 201


@pytest.mark.django_db
def test_get_all_superuser_images(auth_client_super):
    with open(file_path, 'rb') as file:
        auth_client_super.post('/api/v1/images/', data={'file': file})
    response = auth_client_super.get('/api/v1/images/')
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
def test_get_all_user_images(auth_client):
    with open(file_path, 'rb') as file:
        auth_client.post('/api/v1/images/', data={'file': file})
    response = auth_client.get('/api/v1/images/')
    data = response.data
    image = Image.objects.filter(id=1).first()
    image_path = os.path.join(BASE_DIR, 'media', image.image.name)
    if image.uploader.username == "user_Basic":
        assert response.status_code == 200
        assert len(data) == 1
        assert data
        assert os.path.isfile(image_path) == True
        assert data[0]['id'] == 1
        assert len(data[0]['links']) == 1
        assert data[0]['links']['thumbnail_200_link'] == 'http://testserver/media/' + image.image.name + '?height=200'
    elif image.uploader.username == "user_Premium":
        assert response.status_code == 200
        assert len(data) == 1
        assert data
        assert os.path.isfile(image_path) == True
        assert data[0]['id'] == 1
        assert len(data[0]['links']) == 3
        assert data[0]['links']['link_originally_image'] == 'http://testserver/media/'+image.image.name
        assert data[0]['links']['thumbnail_200_link'] == 'http://testserver/media/' + image.image.name + '?height=200'
        assert data[0]['links']['thumbnail_400_link'] == 'http://testserver/media/' + image.image.name + '?height=400'
    else:
        assert response.status_code == 200
        assert len(data) == 1
        assert data
        assert os.path.isfile(image_path) == True
        assert data[0]['id'] == 1
        assert len(data[0]['links']) == 4
        assert data[0]['links']['link_originally_image'] == 'http://testserver/media/' + image.image.name
        assert data[0]['links']['thumbnail_200_link'] == 'http://testserver/media/' + image.image.name + '?height=200'
        assert data[0]['links']['thumbnail_400_link'] == 'http://testserver/media/' + image.image.name + '?height=400'


@pytest.mark.django_db
def test_get_superuser_image(auth_client_super, create_superuser_image):
    response = auth_client_super.get('/media/'+create_superuser_image.image.name)
    assert response.status_code == 200


@pytest.mark.django_db
def test_get_superuser_thumbnail_200(auth_client_super, create_superuser_image):
    response = auth_client_super.get('http://testserver/media/' + create_superuser_image.image.name + '?height=200')
    assert response.status_code == 200


@pytest.mark.django_db
def test_get_superuser_thumbnail_400(auth_client_super, create_superuser_image):
    response = auth_client_super.get('http://testserver/media/'+create_superuser_image.image.name + '?height=400')
    assert response.status_code == 200


@pytest.mark.django_db
def test_get_no_auth_image(auth_client_super, create_superuser_image):
    response1 = auth_client_super.get('http://testserver/media/' + create_superuser_image.image.name)
    auth_client_super.logout()
    response2 = auth_client_super.get('http://testserver/media/'+create_superuser_image.image.name)
    assert response1.status_code == 200
    assert response2.status_code == 403


def delete_images(path):
    files = os.listdir(path)
    for file in files:
        if 'image_for_test_to_DELETE' in file:
            os.remove(os.path.join(path, file))


def test_delete_all_images():
    image_path = os.path.join(BASE_DIR, 'media', 'user_1')
    for height in ['','200','400']:
        delete_images(os.path.join(image_path,height))





