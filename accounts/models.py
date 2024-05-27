from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField()


class Follow(models.Model):
    # followしているユーザー
    follower = models.ForeignKey(User, related_name="following", on_delete=models.CASCADE)
    # followされているユーザー
    followed = models.ForeignKey(User, related_name="being_followed", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("follower", "followed")  # 絶対にfollowerとfollowedは等しくなる
