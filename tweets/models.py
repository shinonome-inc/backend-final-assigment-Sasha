from django.db import models

from accounts.models import User


class Tweet(models.Model):
    content = models.TextField(max_length=280)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class Like(models.Model):
    # likeとuser, tweetのモデル間関係は'one-to-many'
    user = models.ForeignKey(User, related_name="liking_user", on_delete=models.CASCADE)
    tweet = models.ForeignKey(Tweet, related_name="liked_tweet", on_delete=models.CASCADE)

    class Meta:
        unique_together = ("user", "tweet")
