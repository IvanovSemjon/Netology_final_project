from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.serializers import SocialLoginSerializer
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomSocialLoginSerializer(SocialLoginSerializer):
    access_token = serializers.CharField(required=False, allow_blank=True)
    code = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, attrs):
        view = self.context.get('view')
        request = self.context.get('request')
        
        if not view:
            raise serializers.ValidationError('View is not defined')
        
        adapter_class = getattr(view, 'adapter_class', None)
        if not adapter_class:
            raise serializers.ValidationError('Adapter class is not defined in view')
        
        adapter = adapter_class(request)
        
        # Проверяем, передается ли code (для OAuth2) или access_token
        if 'code' in attrs and attrs['code']:
            callback_url = getattr(view, 'callback_url', None)
            client_class = getattr(view, 'client_class', None)
            
            if callback_url and client_class:
                provider = adapter.get_provider()
                client = client_class(
                    request,
                    provider.get_app(request).client_id,
                    provider.get_app(request).secret,
                    adapter.access_token_method,
                    adapter.access_token_url,
                    callback_url,
                    provider.scope,
                )
                # Обмен code на access_token
                token = client.get_access_token(attrs['code'])
                access_token = token['access_token']
            else:
                raise serializers.ValidationError(
                    'Callback URL or Client class is not configured'
                )
        elif 'access_token' in attrs and attrs['access_token']:
            access_token = attrs['access_token']
        else:
            raise serializers.ValidationError(
                'Введите "code" или "access_token"'
            )
        
        # Получаем приложение провайдера
        app = adapter.get_provider().get_app(request)
        
        # Проверяем токен
        token = adapter.parse_token({'access_token': access_token})
        token.app = app
        
        try:
            social_login = adapter.complete_login(request, app, token, response={'access_token': access_token})
            social_login.token = token
        except Exception as e:
            raise serializers.ValidationError(f'Authentication failed: {str(e)}')
        
        if not social_login.is_existing:
            social_login.save(request, connect=True)
        
        # Активируем пользователя
        if not social_login.account.user.is_active:
            social_login.account.user.is_active = True
            social_login.account.user.save()
        
        attrs['user'] = social_login.account.user
        return attrs