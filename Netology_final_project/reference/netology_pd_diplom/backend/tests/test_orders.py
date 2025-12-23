"""Тесты для заказов"""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token
from backend.models import Order, OrderItem, Product, ProductInfo, Shop, Category, Contact
from backend.models.users import User


class OrderTestCase(TestCase):
    """Тесты для работы с заказами"""

    @classmethod
    def setUpTestData(cls):
        # Пользователь
        cls.user = User.objects.create_user(
            email='test@gmail.com',
            password='TestPass123',
            first_name='Тест',
            last_name='Пользователь',
            is_active=True
        )

        # Магазин, категория, товар
        cls.shop = Shop.objects.create(name='Тест Магазин')
        cls.category = Category.objects.create(name='Тест Категория')
        cls.product = Product.objects.create(name='Тест Товар', category=cls.category)
        cls.product_info = ProductInfo.objects.create(
            product=cls.product,
            shop=cls.shop,
            external_id=1,
            price=1000,
            price_rrc=1200,
            quantity=10
        )

        # Контакт
        cls.contact = Contact.objects.create(
            user=cls.user,
            city='Москва',
            street='Тестовая',
            house='1',
            phone='+79001234567'
        )

    def setUp(self):
        self.client = APIClient()
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        self.basket_url = reverse('api:basket')
        self.order_url = reverse('api:order')

    def test_add_to_basket_success(self):
        """Тест добавления товара в корзину"""
        basket_data = {
            'items': [
                {"product_info": self.product_info.id, "quantity": 2}
            ]
        }

        response = self.client.post(self.basket_url, basket_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.json().get('status', False))

        order = Order.objects.get(user=self.user, state='basket')
        self.assertEqual(order.ordered_items.count(), 1)
        order_item = order.ordered_items.first()
        self.assertEqual(order_item.quantity, 2)
        self.assertEqual(order_item.product_info, self.product_info)

    def test_get_basket(self):
        """Тест получения корзины"""
        order = Order.objects.create(user=self.user, state='basket')
        OrderItem.objects.create(order=order, product_info=self.product_info, quantity=1)

        response = self.client.get(self.basket_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['state'], 'basket')

    def test_confirm_order_success(self):
        """Тест подтверждения заказа"""
        order = Order.objects.create(user=self.user, state='basket')
        OrderItem.objects.create(order=order, product_info=self.product_info, quantity=1)

        confirm_data = {
            'id': order.id,
            'contact': self.contact.id
        }

        response = self.client.post(self.order_url, confirm_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.json().get('status', False))

        order.refresh_from_db()
        self.assertEqual(order.state, 'new')
        self.assertEqual(order.contact, self.contact)

    def test_get_orders(self):
        """Тест получения списка заказов"""
        order = Order.objects.create(user=self.user, state='new', contact=self.contact)
        OrderItem.objects.create(order=order, product_info=self.product_info, quantity=1)

        response = self.client.get(self.order_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['state'], 'new')

    def test_unauthorized_access(self):
        """Тест доступа без авторизации"""
        self.client.credentials()  # убираем токен
        response = self.client.get(self.basket_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)