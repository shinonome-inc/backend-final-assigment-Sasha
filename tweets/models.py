from django.db import models


class Tweet(models.Model):
    content = models.TextField(max_length=280)
    created_at = models.DateTimeField(auto_now_add=True)
