from django.db import models

from accounts.models import User


class Tweet(models.Model):
    content = models.TextField(max_length=280)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
