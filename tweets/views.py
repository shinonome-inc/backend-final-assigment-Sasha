from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DeleteView, DetailView, ListView, View

from .models import Like, Tweet


class HomeView(LoginRequiredMixin, ListView):  # LoginRequiredMixinでログインしたユーザーのみhomeにアクセス可能
    model = Tweet
    template_name = "tweets/home.html"
    ordering = ["-created_at"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tweets"] = Tweet.objects.all().select_related("author").prefetch_related("liked_tweet")
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["object"] = (
            Tweet.objects.select_related("author").prefetch_related("liked_tweet").get(pk=self.kwargs["pk"])
        )
        return context


class TweetDeleteView(LoginRequiredMixin, DeleteView):
    model = Tweet
    template_name = "tweets/delete.html"
    success_url = reverse_lazy(settings.LOGIN_REDIRECT_URL)

    def dispatch(self, request, *args, **kwargs):

        tweet = self.get_object()
        if tweet.author != request.user:
            return HttpResponseForbidden("あなたにこのユーザーのツイートを削除する権限はありません。")
        return super().dispatch(request, *args, **kwargs)


@method_decorator(login_required, name="dispatch")
class LikeView(View):

    def post(self, request, *args, **kwargs):
        liked_tweet_pk = self.kwargs["pk"]
        tweet = get_object_or_404(Tweet, pk=liked_tweet_pk)
        user = self.request.user

        like, created = Like.objects.get_or_create(tweet=tweet, user=user)
        if not created:
            return JsonResponse({"error": "Already Liked"}, status=200)

        like_count = tweet.liked_tweet.count()
        return JsonResponse({"status": "liked", "like_count": like_count})


@method_decorator(login_required, name="dispatch")
class UnlikeView(View):

    def post(self, request, *args, **kwargs):
        liked_tweet_pk = self.kwargs["pk"]
        tweet = get_object_or_404(Tweet, pk=liked_tweet_pk)
        user = self.request.user

        try:
            like = Like.objects.get(tweet=tweet, user=user)
            like.delete()
            like_count = tweet.liked_tweet.count()
            return JsonResponse({"status": "unliked", "like_count": like_count})
        except Like.DoesNotExist:
            return JsonResponse({"error": "You cannot unlike this tweet"}, status=200)
