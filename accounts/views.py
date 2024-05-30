from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.http import Http404, HttpResponseBadRequest
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, DeleteView


from tweets.models import Tweet
from .models import Follow, User
from .forms import SignupForm


class SignupView(CreateView):
    form_class = SignupForm
    template_name = "accounts/signup.html"
    success_url = reverse_lazy(settings.LOGIN_REDIRECT_URL)

    def form_valid(self, form):
        response = super().form_valid(form)

        username = form.cleaned_data["username"]
        password = form.cleaned_data["password1"]

        # authenticate関数で認証に使用するため、usernameとpasswordを抜き出した
        user = authenticate(self.request, username=username, password=password)
        login(self.request, user)
        return response


class UserProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = "accounts/user_profile.html"
    pk_url_kwarg = "username"

    # urlパラメータから対象となるユーザーモデルを取得
    def get_object(self, queryset=None):
        username = self.kwargs.get(self.pk_url_kwarg)
        return get_object_or_404(User, username=username)

    # contextを上書きする
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 特定ユーザーtweetのリストをプロフィールに追加する
        user = self.object
        context["specific_user_tweet"] = Tweet.objects.filter(author=user).select_related("author")
        return context


class FollowView(LoginRequiredMixin, CreateView):
    model = Follow
    fields = []
    success_url = reverse_lazy(settings.LOGIN_REDIRECT_URL)
    pk_url_kwarg = "username"

    # 適切なエラーステートメントを自分で設定する
    def get(self, request, *args, **kwargs):
        username = self.kwargs.get(self.pk_url_kwarg)
        # エラーメッセージ1
        try:
            user_to_follow = User.objects.get(username=username)
        except User.DoesNotExist as exc:
            raise Http404("存在しないユーザーをフォローすることはできません。") from exc
        # エラーメッセージ2
        if request.user.id == user_to_follow.id:
            return HttpResponseBadRequest("自分自身をフォローすることは不可能です。")
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        # followerインスタンス = ログインしているユーザー
        form.instance.follower = self.request.user
        # URLからプロフィールのユーザーネームを取得
        followed_username = self.kwargs["username"]
        # followedインスタンス = フォローされたユーザー
        form.instance.followed = User.objects.get(username=followed_username)
        return super().form_valid(form)


class UnFollowView(LoginRequiredMixin, DeleteView):
    model = Follow
    success_url = reverse_lazy(settings.LOGIN_REDIRECT_URL)
    pk_url_kwarg = "username"

    def get_object(self, queryset=None):
        # フォローしているユーザーをリクエストから指定する
        follower = self.request.user
        # フォローされているユーザーをurlパラメータから指定する
        username = self.kwargs.get(self.pk_url_kwarg)
        followed = User.objects.get(username=username)
        return get_object_or_404(Follow, follower=follower, followed=followed)

    # 適切なエラーステートメントを表示させたい
    def get(self, request, *args, **kwargs):
        username = self.kwargs.get(self.pk_url_kwarg)
        try:
            user_to_unfollow = User.objects.get(username=username)
        except User.DoesNotExist as exc:
            raise Http404("存在しないユーザーをアンフォローすることはできません。") from exc
        if request.user.id == user_to_unfollow.id:
            return HttpResponseBadRequest("自分自身をアンフォローすることは不可能です。")
        return super().get(request, *args, **kwargs)
