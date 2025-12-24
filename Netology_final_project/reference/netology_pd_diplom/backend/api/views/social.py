import os
from allauth.socialaccount.providers.github.views import GitHubOAuth2Adapter
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.yandex.views import YandexAuth2Adapter
from allauth.socialaccount.providers.vk.views import VKOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from django.conf import settings
from backend.api.serializers.social import CustomSocialLoginSerializer


class GitHubLogin(SocialLoginView):
    adapter_class = GitHubOAuth2Adapter
    client_class = OAuth2Client
    callback_url = os.getenv('GITHUB_CALLBACK_URL', 
                           settings.SOCIAL_CALLBACK_URLS.get('github', 
                           'http://localhost:8000/accounts/github/login/callback/'))
    serializer_class = CustomSocialLoginSerializer


class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    client_class = OAuth2Client
    callback_url = os.getenv('GOOGLE_CALLBACK_URL', 
                           settings.SOCIAL_CALLBACK_URLS.get('google', 
                           'http://localhost:8000/accounts/google/login/callback/'))
    serializer_class = CustomSocialLoginSerializer


class YandexLogin(SocialLoginView):
    adapter_class = YandexAuth2Adapter
    client_class = OAuth2Client
    callback_url = os.getenv('YANDEX_CALLBACK_URL', 
                           settings.SOCIAL_CALLBACK_URLS.get('yandex', 
                           'http://localhost:8000/accounts/yandex/login/callback/'))
    serializer_class = CustomSocialLoginSerializer


class VKLogin(SocialLoginView):
    adapter_class = VKOAuth2Adapter
    client_class = OAuth2Client
    callback_url = os.getenv('VK_CALLBACK_URL', 
                           settings.SOCIAL_CALLBACK_URLS.get('vk', 
                           'http://localhost:8000/accounts/vk/login/callback/'))
    serializer_class = CustomSocialLoginSerializer