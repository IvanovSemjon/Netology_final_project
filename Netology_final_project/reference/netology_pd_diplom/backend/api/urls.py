from django.urls import path
from django_rest_passwordreset.views import reset_password_request_token, reset_password_confirm
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .views.auth import RegisterAccount, LoginAccount, AccountDetails, ConfirmAccount
from .views.catalog import CategoryView, ShopView, ProductInfoView
from .views.basket import BasketView
from .views.contacts import ContactView
from .views.orders import OrderView
from .views.partners import PartnerUpdate, PartnerState, PartnerOrders
from backend.api.views.admin_import import AdminImportView
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

@api_view(['GET'])
def api_root(request):
    return Response({
        'message': 'Интернет-магазин API v1',
        'endpoints': {
            'categories': '/api/v1/categories/',
            'shops': '/api/v1/shops/',
            'products': '/api/v1/products/',
            'user_register': '/api/v1/user/register/',
            'user_login': '/api/v1/user/login/',
            'basket': '/api/v1/basket/',
            'order': '/api/v1/order/',
        }
    })

app_name = 'api'
urlpatterns = [
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/docs/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    # =======  API Root =====================
    path('', api_root, name='api-root'),
    # =======  Partner endpoints ============
    path('partner/update/', PartnerUpdate.as_view(), name='partner-update'),
    path('partner/state/', PartnerState.as_view(), name='partner-state'),
    path('partner/orders/', PartnerOrders.as_view(), name='partner-orders'),
    path('partner/orders/status/', PartnerOrders.as_view(), name='partner-orders-status'),
    
    # =======  User endpoints ===============
    path('user/register/', RegisterAccount.as_view(), name='user-register'),
    path('user/register/confirm/', ConfirmAccount.as_view(), name='user-register-confirm'),
    path('user/details/', AccountDetails.as_view(), name='user-details'),
    path('user/contact/', ContactView.as_view(), name='user-contact'),
    path('user/login/', LoginAccount.as_view(), name='user-login'),
    path('user/password_reset/', reset_password_request_token, name='password-reset'),
    path('user/password_reset/confirm/', reset_password_confirm, name='password-reset-confirm'),
    
    # =======  Catalog endpoints ============
    path('categories/', CategoryView.as_view(), name='categories'),
    path('shops/', ShopView.as_view(), name='shops'),
    path('products/', ProductInfoView.as_view(), name='products'),
    
    # =======  Order endpoints ==============
    path('basket/', BasketView.as_view(), name='basket'),
    path('order/', OrderView.as_view(), name='order'),
    
    # =======  Admin endpoints ==============
    path('admin/import/', AdminImportView.as_view(), name='admin-import'),
    # path('admin/start-import/', start_import, name='admin-start-import'),
]