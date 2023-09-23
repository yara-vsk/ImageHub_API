import os
from urllib.parse import urlparse, parse_qs
import pytest
from django.core.signing import Signer
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


def extract_signed_url(url):
    parsed_url = urlparse(url)
    query_parameters = parse_qs(parsed_url.query)
    return query_parameters['image_data'][0]


@pytest.mark.django_db
def test_get_all_superuser_images(auth_client_super):
    signer = Signer()

    with open(file_path, 'rb') as file:
        auth_client_super.post('/api/v1/images/', data={'file': file})

    response = auth_client_super.get('/api/v1/images/')
    data = response.data
    image = Image.objects.filter(id=1).first()
    image_path = os.path.join(BASE_DIR, 'media', image.image.name)

    originally_image_data = signer.unsign_object(extract_signed_url(data[0]['links']['link_originally_image']))
    thumbnail_200_link_data = signer.unsign_object(extract_signed_url(data[0]['links']['thumbnail_200_link']))
    thumbnail_400_link_data = signer.unsign_object(extract_signed_url(data[0]['links']['thumbnail_400_link']))
    expiring_link_data = signer.unsign_object(extract_signed_url(data[0]['links']['expiring_link']))

    assert response.status_code == 200
    assert len(data) == 1
    assert data
    assert os.path.isfile(image_path) == True
    assert data[0]['id'] == 1
    assert originally_image_data['path'] == image.image.name
    assert thumbnail_200_link_data['path'] == image.image.name
    assert thumbnail_400_link_data['path'] == image.image.name
    assert expiring_link_data['path'] == image.image.name


@pytest.mark.django_db
def test_get_all_user_images(auth_client):
    signer = Signer()

    with open(file_path, 'rb') as file:
        auth_client.post('/api/v1/images/', data={'file': file})

    response = auth_client.get('/api/v1/images/')
    data = response.data
    image = Image.objects.filter(id=1).first()
    image_path = os.path.join(BASE_DIR, 'media', image.image.name)

    if image.uploader.username == "user_Basic":
        thumbnail_200_link_data = signer.unsign_object(extract_signed_url(data[0]['links']['thumbnail_200_link']))
        assert response.status_code == 200
        assert len(data) == 1
        assert data
        assert os.path.isfile(image_path) == True
        assert data[0]['id'] == 1
        assert len(data[0]['links']) == 1
        assert thumbnail_200_link_data['path'] == image.image.name

    elif image.uploader.username == "user_Premium":
        originally_image_data = signer.unsign_object(extract_signed_url(data[0]['links']['link_originally_image']))
        thumbnail_200_link_data = signer.unsign_object(extract_signed_url(data[0]['links']['thumbnail_200_link']))
        thumbnail_400_link_data = signer.unsign_object(extract_signed_url(data[0]['links']['thumbnail_400_link']))
        assert response.status_code == 200
        assert len(data) == 1
        assert data
        assert os.path.isfile(image_path) == True
        assert data[0]['id'] == 1
        assert len(data[0]['links']) == 3
        assert originally_image_data['path'] == image.image.name
        assert thumbnail_200_link_data['path'] == image.image.name
        assert thumbnail_400_link_data['path'] == image.image.name

    else:
        originally_image_data = signer.unsign_object(extract_signed_url(data[0]['links']['link_originally_image']))
        thumbnail_200_link_data = signer.unsign_object(extract_signed_url(data[0]['links']['thumbnail_200_link']))
        thumbnail_400_link_data = signer.unsign_object(extract_signed_url(data[0]['links']['thumbnail_400_link']))
        expiring_link_data = signer.unsign_object(extract_signed_url(data[0]['links']['expiring_link']))
        assert response.status_code == 200
        assert len(data) == 1
        assert data
        assert os.path.isfile(image_path) == True
        assert data[0]['id'] == 1
        assert len(data[0]['links']) == 4
        assert originally_image_data['path'] == image.image.name
        assert thumbnail_200_link_data['path'] == image.image.name
        assert thumbnail_400_link_data['path'] == image.image.name
        assert expiring_link_data['path'] == image.image.name


@pytest.mark.django_db
def test_get_image_auth_client(client, create_superuser_image, create_user):
    url = '/api/v1/download/'
    url_create_link = '/api/v1/create_expiring_link/'
    data = create_superuser_image.data
    originally_image_signer = extract_signed_url(data['links']['link_originally_image'])
    thumbnail_200_link_signer = extract_signed_url(data['links']['thumbnail_200_link'])
    thumbnail_400_link_signer = extract_signed_url(data['links']['thumbnail_400_link'])
    expiring_link_signer = extract_signed_url(data['links']['expiring_link'])

    client.logout()
    client.login(username=create_user.username, password='test')

    response_originally_image_data = client.get(url, data={'image_data': originally_image_signer})
    response_thumbnail_200_link = client.get(url, data={'image_data': thumbnail_200_link_signer})
    response_thumbnail_400_link = client.get(url, data={'image_data':thumbnail_400_link_signer})
    response_exp_link = client.get(url_create_link, data={'image_data': expiring_link_signer})
    response_exp_link_299 = client.get(url_create_link, data={'image_data': expiring_link_signer,'seconds':299})
    response_exp_link_300 = client.get(url_create_link, data={'image_data': expiring_link_signer,'seconds':300})
    response_exp_link_30000 = client.get(url_create_link, data={'image_data': expiring_link_signer,'seconds':30000})
    response_exp_link_30001 = client.get(url_create_link, data={'image_data': expiring_link_signer,'seconds':30001})

    assert response_originally_image_data.status_code == 200
    assert response_thumbnail_200_link.status_code == 200
    assert response_thumbnail_400_link.status_code == 200
    assert response_exp_link.status_code == 400
    assert response_exp_link_299.status_code == 404
    assert response_exp_link_300.status_code == 404
    assert response_exp_link_30000.status_code == 404
    assert response_exp_link_30001.status_code == 404


@pytest.mark.django_db
def test_create_expiring_link(auth_client_super, create_superuser_image):
    url = '/api/v1/create_expiring_link/'
    data = create_superuser_image.data
    expiring_link_signer = extract_signed_url(data['links']['expiring_link'])
    originally_image_signer = extract_signed_url(data['links']['link_originally_image'])

    response_exp_link = auth_client_super.get(url, data={'image_data': expiring_link_signer})
    response_exp_link_299 = auth_client_super.get(url, data={'image_data': expiring_link_signer,'seconds':299})
    response_exp_link_300 = auth_client_super.get(url, data={'image_data': expiring_link_signer,'seconds':300})
    response_exp_link_300_wrong = auth_client_super.get(url, data={'image_data': originally_image_signer, 'seconds': 300})
    response_exp_link_30000 = auth_client_super.get(url, data={'image_data': expiring_link_signer,'seconds':30000})
    response_exp_link_30001 = auth_client_super.get(url, data={'image_data': expiring_link_signer,'seconds':30001})

    assert response_exp_link.status_code == 400
    assert response_exp_link_299.status_code == 400
    assert response_exp_link_300.status_code == 200
    assert response_exp_link_300_wrong.status_code == 404
    assert response_exp_link_30000.status_code == 200
    assert response_exp_link_30001.status_code == 400

    auth_client_super.logout()
    response_exp_link_300_log_out = auth_client_super.get(url, data={'image_data': expiring_link_signer, 'seconds': 300})
    assert response_exp_link_300_log_out.status_code == 403


@pytest.mark.django_db
def test_get_image_no_auth_client(client, create_superuser_image):
    url = '/api/v1/download/'
    url_create_link = '/api/v1/create_expiring_link/'
    data = create_superuser_image.data
    originally_image_signer = extract_signed_url(data['links']['link_originally_image'])
    thumbnail_200_link_signer = extract_signed_url(data['links']['thumbnail_200_link'])
    thumbnail_400_link_signer = extract_signed_url(data['links']['thumbnail_400_link'])
    expiring_link_signer = extract_signed_url(data['links']['expiring_link'])

    client.logout()
    response_originally_image_data = client.get(url, data={'image_data': originally_image_signer})
    response_thumbnail_200_link = client.get(url, data={'image_data': thumbnail_200_link_signer})
    response_thumbnail_400_link = client.get(url, data={'image_data':thumbnail_400_link_signer})

    assert response_originally_image_data.status_code == 200
    assert response_thumbnail_200_link.status_code == 200
    assert response_thumbnail_400_link.status_code == 200

    client.login(username='test', password='test')
    response_get_exp_link_300 = client.get(url_create_link, data={'image_data': expiring_link_signer, 'seconds': 300})
    exp_link_300_signer = extract_signed_url(response_get_exp_link_300.data['expiring_link'])
    client.logout()
    response_exp_link = client.get(url, data={'image_data': exp_link_300_signer, 'seconds': 300})
    assert response_exp_link.status_code == 200


def delete_images(path):
    files = os.listdir(path)
    for file in files:
        if 'image_for_test_to_DELETE' in file:
            os.remove(os.path.join(path, file))


def test_delete_all_images():
    image_path = os.path.join(BASE_DIR, 'media')
    for user_directory in [us_dir for us_dir in os.listdir(image_path) if us_dir.startswith('user_')]:
        for height in ['','200','400']:
            try:
                delete_images(os.path.join(image_path,user_directory,height))
            except FileNotFoundError:
                continue




