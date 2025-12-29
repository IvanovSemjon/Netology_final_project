from django.urls import path, include
from django.urls import path
from django_rest_passwordreset.views import reset_password_request_token, reset_password_confirm
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views.auth import RegisterAccount, ConfirmAccount
from .views.catalog import CategoryView, ShopView, ProductInfoView
from .views.basket import BasketView
from .views.contacts import ContactView
from .views.orders import OrderView
from .views.partners import PartnerUpdate, PartnerState, PartnerOrders
from backend.api.views.admin_import import AdminImportView
from backend.api.views.user import AccountDetailsWithAvatar

@api_view(['GET'])
def api_root(request):
    return Response({
        'message': 'Интернет-магазин API v1',
        'endpoints': {
            'categories': '/api/v1/categories/',
            'shops': '/api/v1/shops/',
            'products': '/api/v1/products/',
            'user_register': '/api/v1/user/register/',
            'user_jwt_login': '/api/v1/user/jwt/login/',
            'social_auth': '/api/v1/user/social/',
            'basket': '/api/v1/basket/',
            'order': '/api/v1/order/',
        }
    })

app_name = 'api'
urlpatterns = [
    path('', api_root, name='api-root'),

    # =======  Партнеры  ============  
    path('partner/update/', PartnerUpdate.as_view(), name='partner-update'),
    path('partner/state/', PartnerState.as_view(), name='partner-state'),
    path('partner/orders/', PartnerOrders.as_view(), name='partner-orders'),

    # =======  Пользователи  ===============  
    path('user/register/', RegisterAccount.as_view(), name='user-register'),
    path('user/register/confirm/', ConfirmAccount.as_view(), name='user-register-confirm'),
    path('user/contact/', ContactView.as_view(), name='user-contact'),
    path('user/details/', AccountDetailsWithAvatar.as_view(), name='user-details'),
    path('user/password_reset/', reset_password_request_token, name='password-reset'),
    path('user/password_reset/confirm/', reset_password_confirm, name='password-reset-confirm'),

    # JWT authentication
    path('user/jwt/login/', TokenObtainPairView.as_view(), name='jwt-login'),
    path('user/jwt/refresh/', TokenRefreshView.as_view(), name='jwt-refresh'),

    # =======  Каталог ============  
    path('categories/', CategoryView.as_view(), name='categories'),
    path('shops/', ShopView.as_view(), name='shops'),
    path('products/', ProductInfoView.as_view(), name='products'),

    # =======  Заказы ==============  
    path('basket/', BasketView.as_view(), name='basket'),
    path('order/', OrderView.as_view(), name='order'),

    # =======  Админка ==============  
    path('admin/import/', AdminImportView.as_view(), name='admin-import'),

    # =======  Социальные сети ==============  
    path('user/social/', include('backend.api.urls_social')),
]

