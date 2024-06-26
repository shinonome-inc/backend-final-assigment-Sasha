from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView

from tweets.models import Like, Tweet

from .forms import SignupForm
from .models import Follow, User


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
    """
    特定のユーザーに関連するツイート、フォロー状態を表示するビュー
    """

    model = User
    template_name = "accounts/user_profile.html"
    context_object_name = "profile_user"
    pk_url_kwarg = "username"

    def get_object(self, queryset=None):
        # urlパラメータから対象となるユーザーモデルを取得
        username = self.kwargs.get(self.pk_url_kwarg)
        return get_object_or_404(User, username=username)

    # contextを上書きする
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile_user = self.object
        # プロフィールユーザ特有のツイートをcontextに渡す
        context["specific_user_tweets"] = (
            Tweet.objects.filter(author=profile_user).select_related("author").prefetch_related("liked_tweet")
        )
        # フォロー済みであるか調べるためにcontextに渡す
        context["follow"] = Follow.objects.filter(follower=self.request.user, followed=profile_user).exists()
        # プロフィールユーザがフォローしている・されている数
        context["following_num"] = Follow.objects.filter(follower=profile_user).count()
        context["follower_num"] = Follow.objects.filter(followed=profile_user).count()
        context["like_list"] = Like.objects.filter(user=self.request.user).values_list("tweet__pk", flat=True)
        return context


class FollowView(LoginRequiredMixin, CreateView):
    model = Follow
    fields = []
    success_url = reverse_lazy(settings.LOGIN_REDIRECT_URL)
    pk_url_kwarg = "username"

    # 不正なリクエストを最初にdispatchで受け取り、適切なエラーを出力する
    def dispatch(self, request, *args, **kwargs):

        username = self.kwargs.get(self.pk_url_kwarg)
        # エラーメッセージ1
        try:
            user_to_follow = User.objects.get(username=username)
        except User.DoesNotExist as exc:
            raise Http404("存在しないユーザーをフォローすることはできません。") from exc
        # エラーメッセージ2
        if request.user.username == user_to_follow.username:
            return HttpResponseBadRequest("自分自身をフォローすることは不可能です。")

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):

        # URLからプロフィールのユーザーネームを取得
        followed_username = self.kwargs["username"]
        # followerインスタンス = ログインしているユーザー
        form.instance.follower = self.request.user
        # followedインスタンス = フォローされたユーザー
        form.instance.followed = User.objects.get(username=followed_username)

        return super().form_valid(form)


class UnFollowView(LoginRequiredMixin, DeleteView):
    model = Follow
    success_url = reverse_lazy(settings.LOGIN_REDIRECT_URL)
    pk_url_kwarg = "username"

    def dispatch(self, request, *args, **kwargs):
        username = self.kwargs.get(self.pk_url_kwarg)

        try:
            user_to_unfollow = User.objects.get(username=username)
        except User.DoesNotExist as exc:
            raise Http404("存在しないユーザーをアンフォローすることはできません。") from exc

        if request.user.id == user_to_unfollow.id:
            return HttpResponseBadRequest("自分自身をアンフォローすることは不可能です。")

        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):

        # フォローしているユーザーをリクエストから指定する
        follower = self.request.user
        # フォローされているユーザーをurlパラメータから指定する
        username = self.kwargs.get(self.pk_url_kwarg)
        followed = User.objects.get(username=username)

        return get_object_or_404(Follow, follower=follower, followed=followed)


class FollowingListView(LoginRequiredMixin, ListView):
    model = Follow
    template_name = "accounts/following_list.html"
    ordering = ["-created_at"]
    pk_url_kwarg = "username"

    def get_queryset(self):
        """
        プロフィールユーザがフォローしているユーザをDBから取得する
        """
        username = self.kwargs.get(self.pk_url_kwarg)
        profile_user = User.objects.get(username=username)
        return Follow.objects.filter(follower=profile_user).select_related("followed")


class FollowerListView(LoginRequiredMixin, ListView):
    model = Follow
    template_name = "accounts/follower_list.html"
    ordering = ["-created_at"]
    pk_url_kwarg = "username"

    def get_queryset(self):
        """
        プロフィールユーザをフォローしているユーザをDBから取得する
        """
        username = self.kwargs.get(self.pk_url_kwarg)
        profile_user = User.objects.get(username=username)
        return Follow.objects.filter(followed=profile_user).select_related("follower")
