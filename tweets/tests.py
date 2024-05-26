from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Tweet

User = get_user_model()


class TestHomeView(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.login(username="testuser", password="testpassword")
        self.url = reverse("tweets:home")

    def test_success_get(self):

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        # contextに含まれているツイート = DBに保存されているツイートか
        self.assertEqual(list(response.context["tweets"]), list(Tweet.objects.all()))


class TestTweetCreateView(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.login(username="testuser", password="testpassword")
        self.url = reverse("tweets:create")

    def test_success_get(self):

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

    def test_success_post(self):

        valid_form_data = {"content": "This is a test tweet"}
        response = self.client.post(self.url, valid_form_data)

        self.assertRedirects(
            response,
            expected_url=reverse(settings.LOGIN_REDIRECT_URL),
            status_code=302,
            target_status_code=200,
        )
        # DBにデータが追加されているか
        self.assertEqual(Tweet.objects.all().count(), 1)
        # 追加されたデータのcontent = 送信されたcontentか？
        self.assertEqual(Tweet.objects.last().content, valid_form_data["content"])

    def test_failure_post_with_empty_content(self):

        empty_form_data = {"content": ""}
        response = self.client.post(self.url, empty_form_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertIn("このフィールドは必須です。", form.errors["content"])
        self.assertEqual(Tweet.objects.all().count(), 0)

    def test_failure_post_with_too_long_content(self):

        # max lengh text(280)を超えるtextを用意
        too_long_text = ""
        while len(too_long_text) < 290:
            too_long_text += "too long"

        too_long_form_data = {"content": f"{too_long_text}"}
        response = self.client.post(self.url, too_long_form_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertIn("この値は 280 文字以下でなければなりません( 296 文字になっています)。", form.errors["content"])
        self.assertEqual(Tweet.objects.all().count(), 0)


class TestTweetDetailView(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.login(username="testuser", password="testpassword")
        self.tweet = Tweet.objects.create(content="This is a test tweet", author=self.user)
        self.url = reverse("tweets:detail", kwargs={"pk": self.tweet.pk})

    def test_success_get(self):

        response = self.client.get(self.url)

        context_tweets = response.context["object"]
        db_tweets = Tweet.objects.get(pk=self.tweet.pk)  # filterを使用するとquerysetが返される

        self.assertEqual(response.status_code, 200)
        # contextに含まれているツイート = DBに保存されているツイートか
        self.assertEqual(context_tweets, db_tweets)


class TestTweetDeleteView(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.login(username="testuser", password="testpassword")
        self.tweet = Tweet.objects.create(content="This is a test tweet", author=self.user)

    def test_success_post(self):

        url = reverse("tweets:delete", kwargs={"pk": self.tweet.pk})
        response = self.client.post(url)

        self.assertRedirects(
            response,
            expected_url=reverse(settings.LOGIN_REDIRECT_URL),
            status_code=302,
            target_status_code=200,
        )

        self.assertEqual(Tweet.objects.all().count(), 0)
        self.assertFalse(Tweet.objects.filter(pk=self.tweet.pk))

    def test_failure_post_with_not_exist_tweet(self):

        url = reverse("tweets:delete", kwargs={"pk": 999})  # 999 = 存在しないpk
        response = self.client.post(url)

        self.assertEqual(response.status_code, 404)
        self.assertTrue(Tweet.objects.filter(pk=self.tweet.pk))

    def test_failure_post_with_incorrect_user(self):

        # self.userを他のユーザーで上書きして、元のユーザーが作ったtweetを削除しようとしてみる
        self.user = User.objects.create_user(username="testuser2", password="testpassword2")
        self.client.login(username="testuser2", password="testpassword2")

        url = reverse("tweets:delete", kwargs={"pk": self.tweet.pk})  # self.tweetは他のユーザーが作成したtweet
        response = self.client.post(url)

        self.assertEqual(response.status_code, 403)
        self.assertTrue(Tweet.objects.filter(pk=self.tweet.pk))


# class TestLikeView(TestCase):
#     def test_success_post(self):

#     def test_failure_post_with_not_exist_tweet(self):

#     def test_failure_post_with_liked_tweet(self):


# class TestUnLikeView(TestCase):

#     def test_success_post(self):

#     def test_failure_post_with_not_exist_tweet(self):

#     def test_failure_post_with_unliked_tweet(self):
