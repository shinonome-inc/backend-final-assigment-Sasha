from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

from mysite.settings import LOGIN_REDIRECT_URL

from .forms import SignupForm


class SignupView(CreateView):
    form_class = SignupForm
    template_name = "accounts/signup.html"
    success_url = reverse_lazy(LOGIN_REDIRECT_URL)

    def form_valid(self, form):
        response = super().form_valid(form)  # 既に作成したユーザーデータを上書きするため、オーバーライドする
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password1"]
        # authenticate関数で認証に使用するため、usernameとpasswordを抜き出した
        user = authenticate(self.request, username=username, password=password)
        login(self.request, user)
        return response  # 登録後success_urlにリダイレクトさせている


class UserProfileView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/user_profile.html"
