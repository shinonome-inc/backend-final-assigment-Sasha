from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView

from .models import Tweet, Like


class HomeView(LoginRequiredMixin, ListView):  # LoginRequiredMixinでログインしたユーザーのみhomeにアクセス可能
    model = Tweet
    template_name = "tweets/home.html"
    ordering = ["-created_at"]

    def get_context_data(self, **kwargs):
        # homeに全てのtweetを表示させる

        context = super().get_context_data(**kwargs)
        context["tweets"] = Tweet.objects.all().select_related("author")
        return context


class TweetCreateView(LoginRequiredMixin, CreateView):
    model = Tweet
    fields = ["content"]
    template_name = "tweets/create.html"

    success_url = reverse_lazy(settings.LOGIN_REDIRECT_URL)

    def form_valid(self, form):
        # authorを現在ログインしているユーザーに設定
        form.instance.author = self.request.user
        return super().form_valid(form)


class TweetDetailView(LoginRequiredMixin, DetailView):
    model = Tweet
    template_name = "tweets/detail.html"


class TweetDeleteView(LoginRequiredMixin, DeleteView):
    model = Tweet
    template_name = "tweets/delete.html"
    success_url = reverse_lazy(settings.LOGIN_REDIRECT_URL)

    def dispatch(self, request, *args, **kwargs):

        tweet = self.get_object()
        if tweet.author != request.user:
            return HttpResponseForbidden("あなたにこのユーザーのツイートを削除する権限はありません。")
        return super().dispatch(request, *args, **kwargs)


class LikeView(LoginRequiredMixin, CreateView):
    model = Like
    fields = []

    def form_valid(self, form):
        # urlのパラメータからいいね対象のtweetを特定
        likded_tweet_pk = self.kwargs["pk"]
        form.instance.liked_tweet = Tweet.objects.get(pk=likded_tweet_pk)
        # いいねしたユーザー = ログインユーザー
        form.instance.liking_user = self.request.user
        return super().form_valid(form)


class UnlikeView(LoginRequiredMixin, DeleteView):
    model = Like
    pk_url_kwarg = "pk"

    def get_object(self, queryset=None):

        likded_tweet_pk = self.kwargs["pk"]
        likded_tweet = Tweet.objects.get(pk=likded_tweet_pk)

        liking_user = self.request.user
        return get_object_or_404(Like, tweet=likded_tweet, user=liking_user)
