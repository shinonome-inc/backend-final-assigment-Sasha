from django.contrib.auth import SESSION_KEY, get_user_model
from django.test import TestCase
from django.urls import reverse

from mysite.settings import LOGIN_REDIRECT_URL, LOGOUT_REDIRECT_URL

User = get_user_model()


class TestSignupView(TestCase):

    def setUp(self):
        self.url = reverse("accounts:signup")

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
            expected_url=reverse(LOGIN_REDIRECT_URL),
            status_code=302,
            target_status_code=200,
        )

        # 確認2: ユーザーが作成せれるか (DBにレコードが記録されてるか)
        self.assertTrue(User.objects.filter(username=valid_data["username"]).exists())
        # 確認3: ログイン状態になっているか
        self.assertIn(SESSION_KEY, self.client.session)

    # 異常系テストでチェックしたい部分を関数にしてまとめる
    def assert_form_errors_on_signup(self, data, fields_to_check, error_message):
        response = self.client.post(self.url, data)
        form = response.context["form"]

        # homeにリダイレクトはせずに、accounts/signupのURLが再度表示されるだけか確認する
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username=data["username"]).exists())
        self.assertFalse(form.is_valid())

        for field in fields_to_check:
            self.assertIn(error_message, form.errors[field])

    def test_failure_post_with_empty_form(self):
        invalid_data = {
            "username": "",
            "email": "",
            "password1": "",
            "password2": "",
        }

        fields_to_check = ["username", "email", "password1", "password2"]

        self.assert_form_errors_on_signup(invalid_data, fields_to_check, error_message="このフィールドは必須です。")

    def test_failure_post_with_empty_username(self):
        invalid_data = {
            "username": "",
            "email": "test@test.com",
            "password1": "testpassword",
            "password2": "testpassword",
        }

        fields_to_check = ["username"]

        self.assert_form_errors_on_signup(invalid_data, fields_to_check, error_message="このフィールドは必須です。")

    def test_failure_post_with_empty_email(self):
        invalid_data = {
            "username": "testuser",
            "email": "",
            "password1": "testpassword",
            "password2": "testpassword",
        }

        fields_to_check = ["email"]

        self.assert_form_errors_on_signup(invalid_data, fields_to_check, error_message="このフィールドは必須です。")

    def test_failure_post_with_empty_password(self):
        invalid_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "",
            "password2": "",
        }

        fields_to_check = ["password1", "password2"]

        self.assert_form_errors_on_signup(invalid_data, fields_to_check, error_message="このフィールドは必須です。")

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

        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        # 既にユーザーは存在するのでassertTrueとなる
        self.assertTrue(User.objects.filter(username=invalid_data["username"]).exists())
        self.assertFalse(form.is_valid())
        self.assertIn("同じユーザー名が既に登録済みです。", form.errors["username"])

    def test_failure_post_with_invalid_email(self):
        invalid_data = {
            "username": "testuser",
            "email": "testemail",
            "password1": "testpassword",
            "password2": "testpassword",
        }

        fields_to_check = ["email"]

        self.assert_form_errors_on_signup(
            invalid_data, fields_to_check, error_message="有効なメールアドレスを入力してください。"
        )

    def test_failure_post_with_too_short_password(self):
        invalid_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "short",
            "password2": "short",
        }

        fields_to_check = ["password2"]

        self.assert_form_errors_on_signup(
            invalid_data, fields_to_check, error_message="このパスワードは短すぎます。最低 8 文字以上必要です。"
        )

    def test_failure_post_with_password_similar_to_username(self):
        invalid_data = {
            "username": "passwordsimilar",
            "email": "test@test.com",
            "password1": "passwordsimilar",
            "password2": "passwordsimilar",
        }

        fields_to_check = ["password2"]  # password1だとエラーが出る

        self.assert_form_errors_on_signup(
            invalid_data, fields_to_check, error_message="このパスワードは ユーザー名 と似すぎています。"
        )

    def test_failure_post_with_only_numbers_password(self):
        invalid_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "8754321",
            "password2": "8754321",
        }

        fields_to_check = ["password2"]

        self.assert_form_errors_on_signup(
            invalid_data, fields_to_check, error_message="このパスワードは数字しか使われていません。"
        )

    def test_failure_post_with_mismatch_password(self):
        invalid_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "testpassword",
            "password2": "passwordtest",
        }

        fields_to_check = ["password2"]

        self.assert_form_errors_on_signup(
            invalid_data, fields_to_check, error_message="確認用パスワードが一致しません。"
        )


class TestLoginView(TestCase):

    def setUp(self):
        self.url = reverse("accounts:login")
        self.user = User.objects.create_user(username="testuser", email="test@test.com", password="testpassword")

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
            expected_url=reverse(LOGIN_REDIRECT_URL),
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
            expected_url=reverse(LOGOUT_REDIRECT_URL),
            status_code=302,
            target_status_code=200,
        )
        self.assertNotIn(SESSION_KEY, self.client.session)


# class TestUserProfileView(TestCase):
#     def test_success_get(self):


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
