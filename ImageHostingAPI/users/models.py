from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth.models import AbstractUser


class Thumbnail(models.Model):
    size = models.IntegerField(validators=[MinValueValidator(1)])

    def __str__(self):
        return f"Thumbnail({self.size})"


class Tier(models.Model):
    name = models.CharField(max_length=100)
    link_originally_image = models.BooleanField()
    expiring_links = models.BooleanField()
    thumbnail_sizes = models.ManyToManyField(Thumbnail, blank=True)

    def __str__(self):
        return f"Tier({self.name})"


class CustomUser(AbstractUser):
    tier = models.ForeignKey(Tier, on_delete=models.CASCADE)
    REQUIRED_FIELDS =['tier']

    def __str__(self):
        return f"CustomUser(id={self.id})"