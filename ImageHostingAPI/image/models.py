from django.contrib.auth import get_user_model
from django.db import models

# Create your models here.


def user_directory_path(instance, filename):
    return 'user_{0}/{1}'.format(instance.uploader.id, filename)


class Image(models.Model):
    image = models.ImageField(upload_to=user_directory_path)
    uploader = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.image.name}"
