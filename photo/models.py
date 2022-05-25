from urllib import request
import uu
from django.db import models
import uuid

def image_directory_path(instance, filename):
    return '{}/{}'.format(str(uuid.uuid4()), filename)

class Document(models.Model):
    user_id = models.IntegerField()
    email = models.EmailField()
    filename = models.CharField(max_length=255)
    document = models.FileField(upload_to=image_directory_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)