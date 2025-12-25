import requests
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.exceptions import ImmediateHttpResponse
from django.contrib.auth import get_user_model
from django.http import JsonResponse

User = get_user_model()


# ------------------------------
# Адаптер для обычной регистрации
# ------------------------------
class CustomAccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        data = form.cleaned_data
        email = data.get("email")

        # Проверка существующего email
        if email and User.objects.filter(email=email).exists():
            raise ImmediateHttpResponse(
                JsonResponse({
                    "error": True,
                    "code": "email_exists",
                    "message": "Пользователь с таким email уже существует. "
                               "Попробуйте войти через обычную авторизацию или другой соц. аккаунт."
                }, status=400, json_dumps_params={"ensure_ascii": False})
            )

        user.email = email
        user.username = email
        user.first_name = data.get("first_name", "")
        user.last_name = data.get("last_name", "")
        user.company = data.get("company", "")
        user.position = data.get("position", "")
        user.type = data.get("type", "buyer")

        if data.get("password1"):
            user.set_password(data["password1"])
        else:
            user.set_unusable_password()

        user.is_active = True
        if commit:
            user.save()
        return user


# ------------------------------
# Адаптер для соцлогинов (GitHub, Google, Yandex)
# ------------------------------
class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        email = sociallogin.user.email

        # GitHub: вытаскиваем email через API, если пустой
        if sociallogin.account.provider == "github" and not email:
            token = sociallogin.token
            if token:
                resp = requests.get(
                    "https://api.github.com/user/emails",
                    headers={
                        "Authorization": f"token {token.token}",
                        "Accept": "application/vnd.github+json",
                    },
                    timeout=5,
                )
                if resp.status_code == 200:
                    emails = resp.json()
                    primary_email = next(
                        (e["email"] for e in emails if e.get("primary") and e.get("verified")),
                        None,
                    )
                    if primary_email:
                        sociallogin.user.email = primary_email
                        sociallogin.user.username = primary_email
                        email = primary_email

        # Проверка существующего email для всех соцсетей
        if email and User.objects.filter(email=email).exists():
            raise ImmediateHttpResponse(
                JsonResponse({
                    "error": True,
                    "code": "email_exists",
                    "message": "Пользователь с таким email уже существует. "
                               "Попробуйте войти через обычную авторизацию или другой соц. аккаунт."
                }, status=400, json_dumps_params={"ensure_ascii": False})
            )

    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)
        extra = sociallogin.account.extra_data
        provider = sociallogin.account.provider

        if user.email:
            user.username = user.email

        # Заполнение данных пользователя по соцсети
        if provider == "github":
            name = extra.get("name") or ""
            parts = name.split()
            user.first_name = parts[0] if parts else ""
            user.last_name = " ".join(parts[1:]) if len(parts) > 1 else ""
        elif provider == "google":
            user.first_name = extra.get("given_name", "")
            user.last_name = extra.get("family_name", "")
        elif provider == "yandex":
            user.first_name = extra.get("first_name", "")
            user.last_name = extra.get("last_name", "")

        user.type = "buyer"
        user.is_active = True
        return user