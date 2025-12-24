from django.urls import path
from backend.api.views.social import GitHubLogin, GoogleLogin, VKLogin

urlpatterns = [
    path('github/', GitHubLogin.as_view(), name='github_login'),
    path('google/', GoogleLogin.as_view(), name='google_login'),
    path('vk/', VKLogin.as_view(), name='vk_login'),
]