from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView

from .models import Tweet


class HomeView(LoginRequiredMixin, TemplateView):  # LoginRequiredMixinでログインしたユーザーのみhomeにアクセス可能
    template_name = "tweets/home.html"


class TweetCreateView(LoginRequiredMixin, CreateView):
    model = Tweet
    fields = ["content"]
    template_name = "tweets/create.html"

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)  # formのvalid検証とデータベースへの保存
        return response
