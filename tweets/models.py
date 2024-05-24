from django.conf import settings
from django.db import models


class Tweet(models.Model):
    content = models.TextField(max_length=280)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
