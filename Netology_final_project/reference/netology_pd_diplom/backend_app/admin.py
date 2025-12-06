from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import Group
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.admin import TokenAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

from backend.models import (
    User, Shop, Category, Product, ProductInfo, Parameter, 
    ProductParameter, Order, OrderItem, Contact, ConfirmEmailToken
)


# Настройка заголовков админки
admin.site.site_header = "Админка интернет-магазина"
admin.site.site_title = "Управление магазином"
admin.site.index_title = "Панель управления"


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Панель управления пользователями
    """
    model = User
    list_display = ('email', 'first_name', 'last_name', 'type', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('type', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('email', 'first_name', 'last_name', 'company')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password', 'type')}),
        ('Личная информация', {'fields': ('first_name', 'last_name', 'company', 'position')}),
        ('Разрешения', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'type'),
        }),
    )


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    """
    Панель управления магазинами
    """
    list_display = ('name', 'user', 'is_accepting_orders', 'products_count')
    list_filter = ('is_accepting_orders',)
    search_fields = ('name', 'user__email')
    list_editable = ('is_accepting_orders',)
    
    def products_count(self, obj):
        count = obj.product_infos.count()
        if count > 0:
            url = reverse('admin:backend_productinfo_changelist') + f'?shop__id__exact={obj.id}'
            return format_html('<a href="{}">{} товаров</a>', url, count)
        return '0 товаров'
    products_count.short_description = 'Количество товаров'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Панель управления категориями
    """
    list_display = ('id', 'name', 'shops_list', 'products_count')
    search_fields = ('name',)
    filter_horizontal = ('shops',)
    
    def shops_list(self, obj):
        return ', '.join([shop.name for shop in obj.shops.all()])
    shops_list.short_description = 'Магазины'
    
    def products_count(self, obj):
        count = obj.products.count()
        return f'{count} товаров'
    products_count.short_description = 'Количество товаров'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Панель управления товарами
    """
    list_display = ('name', 'category', 'shops_available')
    list_filter = ('category',)
    search_fields = ('name',)
    
    def shops_available(self, obj):
        shops = [info.shop.name for info in obj.product_infos.all()]
        return ', '.join(shops) if shops else 'Нет в продаже'
    shops_available.short_description = 'Доступен в магазинах'


class ProductParameterInline(admin.TabularInline):
    model = ProductParameter
    extra = 1


@admin.register(ProductInfo)
class ProductInfoAdmin(admin.ModelAdmin):
    """
    Панель управления информацией о товарах (склад)
    """
    list_display = ('product', 'shop', 'model', 'price', 'price_rrc', 'quantity', 'availability_status')
    list_filter = ('shop', 'product__category')
    search_fields = ('product__name', 'model', 'shop__name')
    list_editable = ('price', 'price_rrc', 'quantity')
    inlines = [ProductParameterInline]
    
    def availability_status(self, obj):
        if obj.quantity > 10:
            return format_html('<span style="color: green;">✓ В наличии</span>')
        elif obj.quantity > 0:
            return format_html('<span style="color: orange;">⚠ Мало</span>')
        else:
            return format_html('<span style="color: red;">✗ Нет в наличии</span>')
    availability_status.short_description = 'Статус'


@admin.register(Parameter)
class ParameterAdmin(admin.ModelAdmin):
    """
    Панель управления параметрами товаров
    """
    list_display = ('name', 'usage_count')
    search_fields = ('name',)
    
    def usage_count(self, obj):
        count = obj.product_parameters.count()
        return f'Используется в {count} товарах'
    usage_count.short_description = 'Использование'


@admin.register(ProductParameter)
class ProductParameterAdmin(admin.ModelAdmin):
    """
    Панель управления параметрами конкретных товаров
    """
    list_display = ('product_info', 'parameter', 'value')
    list_filter = ('parameter', 'product_info__shop')
    search_fields = ('product_info__product__name', 'parameter__name', 'value')


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('total_price',)
    
    def total_price(self, obj):
        if obj.product_info and obj.quantity:
            return f'{obj.product_info.price * obj.quantity} руб.'
        return '0 руб.'
    total_price.short_description = 'Сумма'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Панель управления заказами
    """
    list_display = ('id', 'user', 'state', 'dt', 'items_count', 'total_sum', 'contact_info')
    list_filter = ('state', 'dt')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    list_editable = ('state',)
    date_hierarchy = 'dt'
    inlines = [OrderItemInline]
    
    def items_count(self, obj):
        return obj.ordered_items.count()
    items_count.short_description = 'Товаров'
    
    def total_sum(self, obj):
        total = sum(item.product_info.price * item.quantity for item in obj.ordered_items.all())
        return f'{total} руб.'
    total_sum.short_description = 'Сумма заказа'
    
    def contact_info(self, obj):
        if obj.contact:
            return f'{obj.contact.city}, {obj.contact.street}'
        return 'Не указан'
    contact_info.short_description = 'Адрес доставки'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """
    Панель управления позициями заказов
    """
    list_display = ('order', 'product_info', 'quantity', 'unit_price', 'total_price')
    list_filter = ('order__state', 'product_info__shop')
    search_fields = ('product_info__product__name', 'order__user__email')
    
    def unit_price(self, obj):
        return f'{obj.product_info.price} руб.'
    unit_price.short_description = 'Цена за единицу'
    
    def total_price(self, obj):
        return f'{obj.product_info.price * obj.quantity} руб.'
    total_price.short_description = 'Общая стоимость'


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    """
    Панель управления контактами пользователей
    """
    list_display = ('user', 'type', 'city', 'street', 'phone')
    list_filter = ('type', 'city')
    search_fields = ('user__email', 'city', 'street', 'phone')


@admin.register(ConfirmEmailToken)
class ConfirmEmailTokenAdmin(admin.ModelAdmin):
    """
    Панель управления токенами подтверждения email
    """
    list_display = ('user', 'key', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__email',)
    readonly_fields = ('key', 'created_at')


# Изменяем названия моделей
Group._meta.verbose_name = 'Группа'
Group._meta.verbose_name_plural = 'Группы'
Token._meta.verbose_name = 'Токен'
Token._meta.verbose_name_plural = 'Токены'