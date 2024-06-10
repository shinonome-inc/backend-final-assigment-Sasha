from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DeleteView, DetailView, ListView, View

from .models import Like, Tweet


class HomeView(LoginRequiredMixin, ListView):  # LoginRequiredMixinでログインしたユーザーのみhomeにアクセス可能
    model = Tweet
    template_name = "tweets/home.html"
    context_object_name = "tweets"
    ordering = ["-created_at"]
    queryset = Tweet.objects.select_related("author").prefetch_related("liked_tweet")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["like_list"] = Like.objects.filter(user=self.request.user).values_list("tweet__pk", flat=True)
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
    context_object_name = "tweet"
    queryset = Tweet.objects.select_related("author").prefetch_related("liked_tweet")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["like_list"] = Like.objects.filter(user=self.request.user).values_list("tweet__pk", flat=True)
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
        tweet_id = kwargs["pk"]
        tweet = get_object_or_404(Tweet, pk=tweet_id)

        like, created = Like.objects.get_or_create(tweet=tweet, user=self.request.user)
        if not created:
            return JsonResponse({"error": "Already Liked"}, status=200)

        server_data = {
            "is_liked": True,
            "tweet_id": tweet_id,
            "unlike_url": reverse("tweets:unlike", kwargs={"pk": tweet_id}),
            "like_count": tweet.liked_tweet.count(),
        }
        return JsonResponse(server_data)


@method_decorator(login_required, name="dispatch")
class UnlikeView(View):

    def post(self, request, *args, **kwargs):
        tweet_id = kwargs["pk"]
        tweet = get_object_or_404(Tweet, pk=tweet_id)
        user = self.request.user

        try:
            like = Like.objects.get(tweet=tweet, user=user)
            like.delete()

            server_data = {
                "is_liked": False,
                "tweet_id": tweet_id,
                "like_url": reverse("tweets:like", kwargs={"pk": tweet_id}),
                "like_count": tweet.liked_tweet.count(),
            }
            return JsonResponse(server_data)
        except Like.DoesNotExist:
            return JsonResponse({"error": "You cannot unlike this tweet"}, status=200)
