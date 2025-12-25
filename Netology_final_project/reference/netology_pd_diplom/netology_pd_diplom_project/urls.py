from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path("admin/", admin.site.urls),

    # REST API authentication - только кастомные эндпоинты
    # path('api/v1/auth/', include('dj_rest_auth.urls')),  # удалить
    # path('api/v1/auth/registration/', include('dj_rest_auth.registration.urls')),  # удалить
    
    # Social authentication (только кастомные)
    # path('api/v1/auth/social/', include('backend.api.urls_social')),

    # allauth - веб-интерфейс
    path('accounts/', include('allauth.urls')),

    # Основное API
    path('api/v1/', include(('backend.api.urls', 'backend'), namespace='backend')),

    # OpenAPI documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # Главная страница
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
]