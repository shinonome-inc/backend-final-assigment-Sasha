from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class HomeView(LoginRequiredMixin, TemplateView):  # LoginRequiredMixinでログインしたユーザーのみhomeにアクセス可能
    login_url = "accounts:login"
    redirect_field_name = "next"  # ログイン後ホームページにリダイレクトされるようにする
    template_name = "tweets/home.html"
