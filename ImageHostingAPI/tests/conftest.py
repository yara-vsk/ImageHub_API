import os

import pytest


from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from image.models import Image
from users.models import Tier, Thumbnail

file_path = os.path.join(os.path.dirname(__file__), 'media_for_tests', 'image_test.jpg')

@pytest.fixture
def create_superuser():
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
    get_user_model().objects.create_superuser(username='test', tier=tier_ent, password='test', email='test@test.test')
    user = get_user_model().objects.filter(id=1).first()
    return user


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def auth_client(create_superuser,client):
    client.login(username='test', password='test')
    return client


@pytest.fixture
def create_superuser_image(create_superuser,auth_client):
    with open(file_path, 'rb') as file:
        auth_client.post('/api/v1/images/', data={'file': file})
    image=Image.objects.filter(id=1).first()
    return image
