from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView

from .models import Tweet


class HomeView(LoginRequiredMixin, ListView):  # LoginRequiredMixinでログインしたユーザーのみhomeにアクセス可能
    model = Tweet
    template_name = "tweets/home.html"

    # homeに全てのtweetを表示させる
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tweets"] = Tweet.objects.all()
        return context


class TweetCreateView(LoginRequiredMixin, CreateView):
    model = Tweet
    fields = ["content"]
    template_name = "tweets/create.html"

    login_url = reverse_lazy(settings.LOGIN_URL)
    success_url = reverse_lazy("accounts:user_profile")

    # 保存処理のついでにログインユーザーをツイートに設定
    def form_valid(self, form):
        tweet_instance = form.save(commit=False)
        tweet_instance.user = self.request.user
        tweet_instance.save()
        return super().form_valid(form)


class TweetDetailView(DetailView):
    model = Tweet
    template_name = "tweets/detail.html"
