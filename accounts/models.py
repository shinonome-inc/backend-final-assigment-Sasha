from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField()  # デフォルトでblank=Falseになっている


# class FriendShip(models.Model):
