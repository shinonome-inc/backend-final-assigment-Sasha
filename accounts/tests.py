from django.conf import settings
from django.contrib.auth import SESSION_KEY, get_user_model
from django.test import TestCase
from django.urls import reverse

from tweets.models import Tweet

from .models import Follow

User = get_user_model()


class TestSignupView(TestCase):

    def setUp(self):
        self.url = reverse("accounts:signup")

    def get_response_and_assert_form_errors_if_invalid_data(self, data, fields_and_error_messages):

        response = self.client.post(self.url, data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(form.is_valid())

        for field, error_message in fields_and_error_messages.items():
            self.assertIn(error_message, form.errors[field])

    def test_success_get(self):

        response = self.client.get(self.url)  # clientからのGETリクエストをシュミレーションする

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response=response, template_name="accounts/signup.html")

    def test_success_post(self):

        valid_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "testpassword",
            "password2": "testpassword",
        }

        response = self.client.post(self.url, valid_data)  # 新規ユーザー登録のPOSTリクエストをシミュレート

        # 確認1: LOGIN_REDIRECT_URLにリダイレクトしているか
        self.assertRedirects(
            response,
            expected_url=reverse(settings.LOGIN_REDIRECT_URL),
            status_code=302,
            target_status_code=200,
        )

        # 確認2: ユーザーが作成せれるか (DBにレコードが記録されてるか)
        self.assertTrue(User.objects.filter(username=valid_data["username"]).exists())
        # 確認3: ログイン状態になっているか
        self.assertIn(SESSION_KEY, self.client.session)

    def test_failure_post_with_empty_form(self):

        invalid_data = {
            "username": "",
            "email": "",
            "password1": "",
            "password2": "",
        }

        fields_and_error_messages = {
            "username": "このフィールドは必須です。",
            "email": "このフィールドは必須です。",
            "password1": "このフィールドは必須です。",
            "password2": "このフィールドは必須です。",
        }

        self.assertFalse(User.objects.filter(username=invalid_data["username"]).exists())
        self.get_response_and_assert_form_errors_if_invalid_data(invalid_data, fields_and_error_messages)

    def test_failure_post_with_empty_username(self):

        invalid_data = {
            "username": "",
            "email": "test@test.com",
            "password1": "testpassword",
            "password2": "testpassword",
        }

        fields_and_error_messages = {
            "username": "このフィールドは必須です。",
        }

        self.assertFalse(User.objects.filter(username=invalid_data["username"]).exists())
        self.get_response_and_assert_form_errors_if_invalid_data(invalid_data, fields_and_error_messages)

    def test_failure_post_with_empty_email(self):

        invalid_data = {
            "username": "testuser",
            "email": "",
            "password1": "testpassword",
            "password2": "testpassword",
        }

        fields_and_error_messages = {
            "email": "このフィールドは必須です。",
        }

        self.assertFalse(User.objects.filter(username=invalid_data["username"]).exists())
        self.get_response_and_assert_form_errors_if_invalid_data(invalid_data, fields_and_error_messages)

    def test_failure_post_with_empty_password(self):

        invalid_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "",
            "password2": "",
        }

        fields_and_error_messages = {
            "password1": "このフィールドは必須です。",
            "password2": "このフィールドは必須です。",
        }

        self.assertFalse(User.objects.filter(username=invalid_data["username"]).exists())
        self.get_response_and_assert_form_errors_if_invalid_data(invalid_data, fields_and_error_messages)

    def test_failure_post_with_duplicated_user(self):
        # 既存のユーザーを作成する
        User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpassword",
        )

        invalid_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "testpassword",
            "password2": "testpassword",
        }

        fields_and_error_messages = {
            "username": "同じユーザー名が既に登録済みです。",
        }

        self.assertTrue(User.objects.filter(username=invalid_data["username"]).exists())
        self.get_response_and_assert_form_errors_if_invalid_data(invalid_data, fields_and_error_messages)

    def test_failure_post_with_invalid_email(self):

        invalid_data = {
            "username": "testuser",
            "email": "testemail",
            "password1": "testpassword",
            "password2": "testpassword",
        }

        fields_and_error_messages = {
            "email": "有効なメールアドレスを入力してください。",
        }

        self.assertFalse(User.objects.filter(username=invalid_data["username"]).exists())
        self.get_response_and_assert_form_errors_if_invalid_data(invalid_data, fields_and_error_messages)

    def test_failure_post_with_too_short_password(self):

        invalid_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "short",
            "password2": "short",
        }

        fields_and_error_messages = {
            "password2": "このパスワードは短すぎます。最低 8 文字以上必要です。",
        }

        self.assertFalse(User.objects.filter(username=invalid_data["username"]).exists())
        self.get_response_and_assert_form_errors_if_invalid_data(invalid_data, fields_and_error_messages)

    def test_failure_post_with_password_similar_to_username(self):

        invalid_data = {
            "username": "passwordsimilar",
            "email": "test@test.com",
            "password1": "passwordsimilar",
            "password2": "passwordsimilar",
        }

        fields_and_error_messages = {
            "password2": "このパスワードは ユーザー名 と似すぎています。",
        }

        self.assertFalse(User.objects.filter(username=invalid_data["username"]).exists())
        self.get_response_and_assert_form_errors_if_invalid_data(invalid_data, fields_and_error_messages)

    def test_failure_post_with_only_numbers_password(self):

        invalid_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "8754321",
            "password2": "8754321",
        }

        fields_and_error_messages = {
            "password2": "このパスワードは数字しか使われていません。",
        }

        self.assertFalse(User.objects.filter(username=invalid_data["username"]).exists())
        self.get_response_and_assert_form_errors_if_invalid_data(invalid_data, fields_and_error_messages)

    def test_failure_post_with_mismatch_password(self):

        invalid_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "testpassword",
            "password2": "passwordtest",
        }

        fields_and_error_messages = {
            "password2": "確認用パスワードが一致しません。",
        }

        self.assertFalse(User.objects.filter(username=invalid_data["username"]).exists())
        self.get_response_and_assert_form_errors_if_invalid_data(invalid_data, fields_and_error_messages)


class TestLoginView(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", email="test@test.com", password="testpassword")
        self.url = reverse("accounts:login")

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_success_post(self):
        valid_data = {
            "username": "testuser",
            "password": "testpassword",
        }

        response = self.client.post(self.url, valid_data)
        # 確認1: LOGIN_REDIRECT_URLにリダイレクトされるか
        self.assertRedirects(
            response,
            expected_url=reverse(settings.LOGIN_REDIRECT_URL),
            status_code=302,
            target_status_code=200,
        )
        # 確認2: ログイン状態になっているか
        self.assertIn(SESSION_KEY, self.client.session)

    def test_failure_post_with_not_exists_user(self):

        invalid_data = {
            "username": "nonexistentuser",
            "password": "testpassword",
        }

        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "正しいユーザー名とパスワードを入力してください。どちらのフィールドも大文字と小文字は区別されます。",
            form.errors["__all__"],
        )
        self.assertNotIn(SESSION_KEY, self.client.session)

    def test_failure_post_with_empty_password(self):

        invalid_data = {
            "username": "testuser",
            "password": "",
        }

        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertIn("このフィールドは必須です。", form.errors["password"])
        self.assertNotIn(SESSION_KEY, self.client.session)


class TestLogoutView(TestCase):

    def setUp(self):
        self.url = reverse("accounts:logout")

    def test_success_post(self):
        response = self.client.post(self.url)

        self.assertRedirects(
            response,
            expected_url=reverse(settings.LOGOUT_REDIRECT_URL),
            status_code=302,
            target_status_code=200,
        )
        self.assertNotIn(SESSION_KEY, self.client.session)


class TestUserProfileView(TestCase):

    def setUp(self):

        # user1がuser2をフォローしている
        # 想定: user1が自分のプロフィール画面を見ている
        self.user1 = User.objects.create_user(username="testuser1", email="test1@test.com", password="testpassword1")
        self.user2 = User.objects.create_user(username="testuser2", email="test2@test.com", password="testpassword2")
        Follow.objects.create(follower=self.user1, followed=self.user2)

        self.client.login(username="testuser1", password="testpassword1")
        # urlpatternがusernameを含むので
        self.url = reverse("accounts:user_profile", kwargs={"username": self.user1.username})

    def test_success_get(self):

        response = self.client.get(self.url)

        # context内のツイートとdb内のツイートを準備
        context_tweets = response.context["specific_user_tweets"]
        db_tweets = Tweet.objects.filter(author=self.user1)

        # context内のフォロー・フォロワー数(user1)
        context_following_num = response.context["following_num"]
        context_follower_num = response.context["follower_num"]
        # DB内のフォロー・フォロワー数(user1)
        db_following_num = Follow.objects.filter(follower=self.user1, followed=self.user2).count()
        db_follower_num = Follow.objects.filter(follower=self.user2, followed=self.user1).count()

        # context内のツイート一覧 = DB内にある該当ユーザーのツイート一覧になるか？
        self.assertEqual(list(context_tweets), list(db_tweets))
        # context内のフォロー数 = DB内のフォロー数?
        self.assertEqual(context_following_num, db_following_num)
        # context内のフォロワー数 = DB内のフォロワー数?
        self.assertEqual(context_follower_num, db_follower_num)


class TestFollowView(TestCase):

    def setUp(self):
        # 想定: ログイン状態のuser1がuser2をフォローする
        self.user1 = User.objects.create_user(username="testuser1", email="test1@test.com", password="testpassword1")
        self.user2 = User.objects.create_user(username="testuser2", email="test2@test.com", password="testpassword2")
        self.client.login(username="testuser1", password="testpassword1")
        self.url = reverse("accounts:follow", kwargs={"username": self.user2.username})

    def test_success_post(self):

        response = self.client.post(self.url)

        self.assertRedirects(
            response,
            expected_url=reverse(settings.LOGIN_REDIRECT_URL),
            status_code=302,
            target_status_code=200,
        )

        self.assertEqual(Follow.objects.all().count(), 1)

    def test_failure_post_with_not_exist_user(self):

        # 存在しないユーザーネームをURLパラメータに指定する
        nonexistent_username_url = reverse("accounts:follow", kwargs={"username": "nonexistentusername"})
        response = self.client.post(nonexistent_username_url)

        self.assertEqual(response.status_code, 404)
        self.assertFalse(Follow.objects.all().exists())

    def test_failure_post_with_self(self):

        self_username_url = reverse("accounts:follow", kwargs={"username": self.user1.username})
        response = self.client.post(self_username_url)

        self.assertEqual(response.status_code, 400)
        self.assertFalse(Follow.objects.all().exists())


class TestUnfollowView(TestCase):

    def setUp(self):
        # user1がuser2をフォローしている
        # user1がuser2のプロフィール画面でアンフォローする
        self.user1 = User.objects.create_user(username="testuser1", email="test1@test.com", password="testpassword1")
        self.user2 = User.objects.create_user(username="testuser2", email="test2@test.com", password="testpassword2")
        Follow.objects.create(follower=self.user1, followed=self.user2)
        self.client.login(username="testuser1", password="testpassword1")

    def test_success_post(self):

        valid_url = reverse("accounts:unfollow", kwargs={"username": self.user2.username})
        response = self.client.post(valid_url)

        self.assertRedirects(
            response,
            expected_url=reverse(settings.LOGIN_REDIRECT_URL),
            target_status_code=200,
        )
        self.assertEqual(Follow.objects.all().count(), 0)

    def test_failure_post_with_not_exist_user(self):

        nonexistent_username_url = reverse("accounts:unfollow", kwargs={"username": "nonexistentusername"})
        response = self.client.post(nonexistent_username_url)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(Follow.objects.all().count(), 1)

    def test_failure_post_with_self(self):

        self_username_url = reverse("accounts:follow", kwargs={"username": self.user1.username})

        response = self.client.post(self_username_url)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Follow.objects.all().count(), 1)


class TestFollowingListView(TestCase):

    def setUp(self):
        # 想定: ログイン状態のuser1が、自分のフォローしているuser2を一覧で見る
        self.user1 = User.objects.create_user(username="testuser1", email="test1@test.com", password="testpassword1")
        self.user2 = User.objects.create_user(username="testuser2", email="test2@test.com", password="testpassword2")
        Follow.objects.create(follower=self.user1, followed=self.user2)

        self.client.login(username="testuser1", password="testpassword1")
        self.url = reverse("accounts:following_list", kwargs={"username": self.user1.username})

    def test_success_get(self):

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)


class TestFollowerListView(TestCase):
    # 想定: user1がフォローしていたuser2をアンフォローする
    def setUp(self):

        self.user1 = User.objects.create_user(username="testuser1", email="test1@test.com", password="testpassword1")
        self.user2 = User.objects.create_user(username="testuser2", email="test2@test.com", password="testpassword2")
        # 一覧で表示するために、Followインスタンスを作成
        Follow.objects.create(follower=self.user1, followed=self.user2)
        self.client.login(username="testuser1", password="testpassword1")
        self.url = reverse("accounts:follower_list", kwargs={"username": self.user1.username})

    def test_success_get(self):

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
