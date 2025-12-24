from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomAccountAdapter(DefaultAccountAdapter):
    """Кастомный адаптер для аккаунтов с поддержкой вашей модели User."""
    
    def save_user(self, request, user, form, commit=True):
        """Сохраняет пользователя с дополнительными полями вашей модели."""
        data = form.cleaned_data
        user.email = data.get('email')
        user.first_name = data.get('first_name', '')
        user.last_name = data.get('last_name', '')
        user.company = data.get('company', '')
        user.position = data.get('position', '')
        user.type = data.get('type', 'buyer')
        
        user.username = data.get('email', '')
        
        if 'password1' in data:
            user.set_password(data['password1'])
        else:
            user.set_unusable_password()
        
        if not user.is_active:
            user.is_active = True
        
        if commit:
            user.save()
        return user


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """Кастомный адаптер для социальных аккаунтов с поддержкой вашей модели."""
    
    def populate_user(self, request, sociallogin, data):
        """Заполняет данные пользователя из социального аккаунта."""
        user = super().populate_user(request, sociallogin, data)
        
        if user.email:
            user.username = user.email
        
        extra_data = sociallogin.account.extra_data
        
        if sociallogin.account.provider == 'github':
            user.first_name = extra_data.get('name', '').split(' ')[0] if extra_data.get('name') else ''
            user.last_name = ' '.join(extra_data.get('name', '').split(' ')[1:]) if extra_data.get('name') else ''
        
        elif sociallogin.account.provider == 'google':
            user.first_name = extra_data.get('given_name', '')
            user.last_name = extra_data.get('family_name', '')
        
        elif sociallogin.account.provider == 'vk':
            user.first_name = extra_data.get('first_name', '')
            user.last_name = extra_data.get('last_name', '')
        
        elif sociallogin.account.provider == 'yandex':
            user.first_name = extra_data.get('first_name', '')
            user.last_name = extra_data.get('last_name', '')
        
        # Устанавливаем тип пользователя по умолчанию
        user.type = 'buyer'
        user.is_active = True  # Активируем пользователя
        
        return user