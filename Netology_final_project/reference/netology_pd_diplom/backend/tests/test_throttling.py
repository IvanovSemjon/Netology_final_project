from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase, APIClient


User = get_user_model()


class ThrottlingTests(APITestCase):
    """
    Проверка:
    - AnonRateThrottle
    - UserRateThrottle
    - ScopedRateThrottle
    """

    def setUp(self):
        cache.clear()

        self.client = APIClient()

        self.user = User.objects.create_user(
            email="user@test.com",
            password="testpassword123",
            first_name="Test",
            last_name="User",
            is_active=True,
        )

        self.token = Token.objects.create(user=self.user)

        self.auth_headers = {
            "HTTP_AUTHORIZATION": f"Token {self.token.key}"
        }

        self.categories_url = "/api/v1/categories/"
        self.basket_url = "/api/v1/basket/"


    def test_anon_rate_throttle(self):
        """
        anon = 17/day
        """
        for _ in range(17):
            response = self.client.get(self.categories_url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(self.categories_url)
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)


    def test_user_rate_throttle(self):
        """
        user = 111/day
        """
        for _ in range(111):
            response = self.client.get(
                self.categories_url,
                **self.auth_headers
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(
            self.categories_url,
            **self.auth_headers
        )
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)


    def test_scoped_rate_throttle_basket(self):
        """
        basket = 5/min
        """
        for _ in range(5):
            response = self.client.get(
                self.basket_url,
                **self.auth_headers
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(
            self.basket_url,
            **self.auth_headers
        )
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)