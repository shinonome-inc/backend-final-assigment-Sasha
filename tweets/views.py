from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView

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
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)
