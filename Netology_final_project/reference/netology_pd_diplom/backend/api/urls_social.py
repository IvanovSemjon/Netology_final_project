from django.urls import path
from backend.api.views.social import GitHubLogin, GoogleLogin, YandexLogin

urlpatterns = [
    path("github/", GitHubLogin.as_view(), name="github_login"),
    path("google/", GoogleLogin.as_view(), name="google_login"),
    path("yandex/", YandexLogin.as_view(), name="yandex_login"),
]