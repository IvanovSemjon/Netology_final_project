"""
Загрузка данных.
"""

import yaml
from backend.models import (
    Category,
    Parameter,
    Product,
    ProductInfo,
    ProductParameter,
    Shop,
)
from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    """
    Загрузка данных для магазина из YAML файла.
    """

    help = "Загрузка данных из YAML файла"

    def add_arguments(self, parser):
        """
        Парсер аргументов командной строки.
        """
        parser.add_argument("file_path", type=str, help="Путь к YAML файлу")

    def handle(self, *args, **options):
        """
        Работа с файлом.
        """
        file_path = options["file_path"]

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                data = yaml.safe_load(file)

            if not data:
                self.stdout.write(
                    self.style.ERROR(f"Файл {file_path} пуст или некорректен")
                )
                return

            shop, created = Shop.objects.get_or_create(
                name=data.get("shop", f"Магазин без имени"),
                defaults={"is_accepting_orders": True},
            )
            if created:
                self.stdout.write(f"Создан магазин: {shop.name}")


            for category_data in data.get("categories", []):
                category, created = Category.objects.get_or_create(
                    id=category_data.get("id"),
                    defaults={"name": category_data.get("name", "Без имени")},
                )
                category.shops.add(shop)
                if created:
                    self.stdout.write(f"Создана категория: {category.name}")

            # Удаляем старые товары магазина
            ProductInfo.objects.filter(shop=shop).delete()

            created_count = 0
            errors = []

            # Создаем товары
            for item in data.get("goods", []):
                try:
                    with transaction.atomic():
                        product, _ = Product.objects.get_or_create(
                            name=item.get("name", "Неизвестный товар"),
                            category_id=item.get("category"),
                        )

                        product_info = ProductInfo.objects.create(
                            product=product,
                            external_id=item.get("id"),
                            model=item.get("model", ""),
                            price=item.get("price", 0),
                            price_rrc=item.get("price_rrc", 0),
                            quantity=item.get("quantity", 0),
                            shop=shop,
                        )

                        for name, value in item.get("parameters", {}).items():
                            parameter, _ = Parameter.objects.get_or_create(name=name)
                            ProductParameter.objects.create(
                                product_info=product_info,
                                parameter=parameter,
                                value=value,
                            )

                        created_count += 1
                        self.stdout.write(f"Загружен товар: {product.name}")
                except Exception as e:
                    errors.append(f"{item.get('name', 'Unknown')}: {e}")
                    continue

            self.stdout.write(
                self.style.SUCCESS(
                    f"Данные успешно загружены. Товаров создано: {created_count}"
                )
            )
            if errors:
                self.stdout.write(
                    self.style.WARNING(
                        f"Ошибки при загрузке некоторых товаров: {errors[:5]}"
                    )
                )

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"Файл {file_path} не найден"))
        except yaml.YAMLError as e:
            self.stdout.write(self.style.ERROR(f"Ошибка парсинга YAML: {e}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Ошибка загрузки данных: {e}"))
