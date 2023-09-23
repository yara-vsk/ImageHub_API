import os
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from users.models import Tier, Thumbnail

file_path = os.path.join(os.path.dirname(__file__), 'media_for_tests', 'image_for_test_to_DELETE.jpg')


@pytest.fixture
def create_tiers():
    thumbnail_200 = Thumbnail.objects.create(size=200)
    thumbnail_400 = Thumbnail.objects.create(size=400)
    tier_bas = Tier.objects.create(name='Basic', link_originally_image=False, expiring_links=False)
    tier_prem = Tier.objects.create(name='Premium', link_originally_image=True, expiring_links=False)
    tier_ent = Tier.objects.create(name='Enterprise', link_originally_image=True, expiring_links=True)
    tier_bas.thumbnail_sizes.add(thumbnail_200)
    tier_prem.thumbnail_sizes.add(thumbnail_200, thumbnail_400)
    tier_ent.thumbnail_sizes.add(thumbnail_200, thumbnail_400)
    tier_bas.save()
    tier_prem.save()
    tier_ent.save()
    return {'Basic':tier_bas,
            'Premium':tier_prem,
            'Enterprise':tier_ent}


@pytest.fixture
def create_superuser(create_tiers):
    tier = create_tiers['Enterprise']
    get_user_model().objects.create_superuser(username='test', tier=tier, password='test', email='test@test.test')
    superuser = get_user_model().objects.filter(id=1).first()
    return superuser


@pytest.fixture(params=['Basic', 'Premium', 'Enterprise'])
def create_user(request, create_tiers):
    tier = create_tiers[request.param]
    user = get_user_model().objects.create_user(username='user_'+str(request.param), tier=tier, password='test', email='user_'+str(request.param)+'@test.test')
    return user


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def auth_client_super(create_superuser, client):
    client.login(username='test', password='test')
    return client


@pytest.fixture
def auth_client(create_user, client):
    client.login(username=create_user.username, password='test')
    return client


@pytest.fixture
def create_superuser_image(auth_client_super):
    with open(file_path, 'rb') as file:
        response = auth_client_super.post('/api/v1/images/', data={'file': file})
    return response
