from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.


class Thumbnail(models.Model):
    size = models.IntegerField()

    def __str__(self):
        return str(self.size)


class Tier(models.Model):
    name = models.CharField(max_length=100)
    link_originally_image = models.BooleanField()
    expiring_links = models.BooleanField()
    thumbnail_sizes = models.ManyToManyField(Thumbnail)

    def __str__(self):
        return self.name


class CustomUser(AbstractUser):
    tier = models.ForeignKey(Tier, on_delete=models.CASCADE)
    REQUIRED_FIELDS =['tier']

    def __str__(self):
        return self.username