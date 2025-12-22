"""
Django management команда для загрузки данных магазинов из YAML файлов.
"""

import os

import yaml
from backend.models import (
    Category,
    Parameter,
    Product,
    ProductInfo,
    ProductParameter,
    Shop,
)
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    """
    Загрузка данных магазинов из YAML файла.
    Пример использования:
    python manage.py load_shop_data --file shop1.yaml
    python manage.py load_shop_data --all
    """

    help = "Загрузка данных магазинов из YAML файлов"

    def add_arguments(self, parser):
        parser.add_argument("--file", type=str, help="Путь к YAML файлу для загрузки")
        parser.add_argument(
            "--all",
            action="store_true",
            help="Загрузить все файлы shop*.yaml из папки data",
        )

    def handle(self, *args, **options):
        if options.get("file"):
            self.load_file(options["file"])
        elif options.get("all"):
            self.load_all_files()
        else:
            self.stdout.write(self.style.ERROR("Укажите --file или --all"))

    def load_all_files(self):
        data_dir = os.path.join(settings.BASE_DIR, "data")
        if not os.path.exists(data_dir):
            self.stdout.write(self.style.ERROR(f"Папка {data_dir} не найдена"))
            return

        yaml_files = [
            f
            for f in os.listdir(data_dir)
            if f.startswith("shop") and f.endswith(".yaml")
        ]
        if not yaml_files:
            self.stdout.write(self.style.WARNING("Файлы shop*.yaml не найдены"))
            return

        for filename in yaml_files:
            filepath = os.path.join(data_dir, filename)
            self.stdout.write(f"Загружаю {filename}...")
            self.load_file(filepath)

    def load_file(self, filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as file:
                data = yaml.safe_load(file)

            if not data:
                self.stdout.write(
                    self.style.WARNING(f"Файл {filepath} пуст или некорректен")
                )
                return

            self.process_shop_data(data)
            self.stdout.write(
                self.style.SUCCESS(f"Данные из {filepath} успешно загружены")
            )

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"Файл {filepath} не найден"))
        except yaml.YAMLError as e:
            self.stdout.write(self.style.ERROR(f"Ошибка парсинга YAML: {e}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Ошибка загрузки: {e}"))

    def process_shop_data(self, data):
        shop_name = data.get("shop", "Без имени")
        shop, created = Shop.objects.get_or_create(
            name=shop_name, defaults={"is_accepting_orders": True}
        )
        self.stdout.write(
            f'{"Создан" if created else "Обновляется"} магазин: {shop.name}'
        )

        for category_data in data.get("categories", []):
            category, cat_created = Category.objects.get_or_create(
                id=category_data.get("id"),
                defaults={"name": category_data.get("name", "Без имени")},
            )
            category.shops.add(shop)
            if cat_created:
                self.stdout.write(f"  Создана категория: {category.name}")

        ProductInfo.objects.filter(shop=shop).delete()
        self.stdout.write(f"  Удалены старые товары магазина {shop.name}")

        created_count = 0
        errors = []

        for item in data.get("goods", []):
            try:
                with transaction.atomic():
                    product, _ = Product.objects.get_or_create(
                        name=item.get("name", "Неизвестный товар"),
                        defaults={"category_id": item.get("category")},
                    )

                    product_info = ProductInfo.objects.create(
                        product=product,
                        shop=shop,
                        external_id=item.get("id"),
                        model=item.get("model", ""),
                        price=item.get("price", 0),
                        price_rrc=item.get("price_rrc", 0),
                        quantity=item.get("quantity", 0),
                    )

                    for param_name, param_value in item.get("parameters", {}).items():
                        parameter, _ = Parameter.objects.get_or_create(name=param_name)
                        ProductParameter.objects.create(
                            product_info=product_info,
                            parameter=parameter,
                            value=str(param_value),
                        )

                    created_count += 1
                    self.stdout.write(f"    Загружен товар: {product.name}")
            except Exception as e:
                errors.append(f"{item.get('name', 'Unknown')}: {e}")
                self.stdout.write(
                    self.style.WARNING(
                        f'    Ошибка товара {item.get("name", "Unknown")}: {e}'
                    )
                )

        self.stdout.write(self.style.SUCCESS(f"  Товаров создано: {created_count}"))
        if errors:
            self.stdout.write(
                self.style.WARNING(
                    f'  Ошибки при загрузке товаров: {errors[:5]}{"..." if len(errors) > 5 else ""}'
                )
            )
