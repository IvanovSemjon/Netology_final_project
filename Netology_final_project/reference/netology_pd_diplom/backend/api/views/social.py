from dj_rest_auth.registration.views import SocialLoginView

from allauth.socialaccount.providers.github.views import GitHubOAuth2Adapter
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.yandex.views import YandexOAuth2Adapter


class GitHubLogin(SocialLoginView):
    adapter_class = GitHubOAuth2Adapter


class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter


class YandexLogin(SocialLoginView):
    adapter_class = YandexOAuth2Adapter