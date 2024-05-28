from django.conf import settings
from django.contrib.auth import SESSION_KEY, get_user_model
from django.test import TestCase
from django.urls import reverse

from tweets.models import Tweet

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
        # ユーザーを作成
        self.user = User.objects.create_user(username="testuser", email="test@test.com", password="testpassword")
        # ログインさせる
        self.client.login(username="testuser", password="testpassword")

        # urlpatternがusernameを含むので
        self.url = reverse("accounts:user_profile", kwargs={"username": self.user.username})

    def test_success_get(self):

        response = self.client.get(self.url)

        # context内のツイートとdb内のツイートを準備
        context_tweets = response.context["user_tweets"]
        db_tweets = Tweet.objects.filter(author=self.user)

        # context内のツイート一覧 = DB内にある該当ユーザーのツイート一覧になるか？
        self.assertEqual(list(context_tweets), list(db_tweets))


# class TestUserProfileEditView(TestCase):
#     def test_success_get(self):

#     def test_success_post(self):

#     def test_failure_post_with_not_exists_user(self):

#     def test_failure_post_with_incorrect_user(self):


# class TestFollowView(TestCase):
#     def test_success_post(self):

#     def test_failure_post_with_not_exist_user(self):

#     def test_failure_post_with_self(self):


# class TestUnfollowView(TestCase):
#     def test_success_post(self):

#     def test_failure_post_with_not_exist_tweet(self):

#     def test_failure_post_with_incorrect_user(self):


# class TestFollowingListView(TestCase):
#     def test_success_get(self):


# class TestFollowerListView(TestCase):
#     def test_success_get(self):
