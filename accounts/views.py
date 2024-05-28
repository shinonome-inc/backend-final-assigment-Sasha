from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponseBadRequest
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView

from tweets.models import Tweet

from .forms import SignupForm
from .models import Follow, User


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
    context_object_name = "user_tweets"

    # URLから取得したusernameに関連するツイートのみを表示
    def get_queryset(self):

        username = self.kwargs["username"]
        # n+1問題を防止する
        return Tweet.objects.filter(author__username=username).select_related("author")


class FollowView(LoginRequiredMixin, CreateView):
    model = Follow
    fields = []
    success_url = reverse_lazy(settings.LOGIN_REDIRECT_URL)

    # 適切なエラーステートメントを自分で設定する
    def dispatch(self, request, *args, **kwargs):
        follow = self.get_object()

        if not follow.followed:
            raise Http404("存在しないユーザーをフォローすることはできません。")
        elif follow.followed == follow.follower:
            return HttpResponseBadRequest("自分自身をフォローすることは不可能です。")
        return super().dispatch(request, *args, **kwargs)

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

    # 適切なエラーステートメントを自分で設定する
    def dispatch(self, request, *args, **kwargs):
        follow = self.get_object()

        if not follow.followed:
            raise Http404("存在しないユーザーをフォローすることはできません。")
        elif follow.followed == follow.follower:
            return HttpResponseBadRequest("自分自身をフォローすることは不可能です。")
        return super().dispatch(request, *args, **kwargs)
