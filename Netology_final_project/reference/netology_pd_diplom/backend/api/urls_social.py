from django.urls import path
from backend.api.views.social import GitHubLogin, GoogleLogin, YandexLogin

app_name = 'social'

urlpatterns = [
    path('github/', GitHubLogin.as_view(), name='user-github-login'),
    path('google/', GoogleLogin.as_view(), name='user-google-login'),
    path('yandex/', YandexLogin.as_view(), name='user-yandex-login'),
]