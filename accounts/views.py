from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView
from .forms import SignupForm


class SignupView(CreateView):
    form_class = SignupForm
    template_name = "accounts/signup.html"
    success_url = reverse_lazy(settings.LOGIN_REDIRECT_URL)

    def form_valid(self, form):
        response = super().form_valid(form)  # 既に作成したユーザーデータを上書きするため、オーバーライドする
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password1"]
        # authenticate関数で認証に使用するため、usernameとpasswordを抜き出した
        user = authenticate(self.request, username=username, password=password)
        login(self.request, user)
        return response  # 登録後success_urlにリダイレクトさせている


class UserProfileView(LoginRequiredMixin, ListView):
    model = Tweet
    template_name = "accounts/user_profile.html"

    # URLから取得したusernameに関連するツイートのみを表示
    def get_queryset(self):
        username = self.kwargs["username"]
        # 関連するユーザーモデルのusernameフィールドを使って絞り込む
        # author=usernameだとエラーが出る
        return Tweet.objects.filter(author__username=username)
