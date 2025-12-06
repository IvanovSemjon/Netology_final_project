"""
Django management команда для загрузки данных магазинов из YAML файлов
"""
import os
import yaml
from django.core.management.base import BaseCommand
from django.conf import settings
from backend.models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter


class Command(BaseCommand):
    help = 'Загрузка данных магазинов из YAML файлов'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            help='Путь к YAML файлу для загрузки'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Загрузить все файлы shop*.yaml из папки data'
        )

    def handle(self, *args, **options):
        if options['file']:
            self.load_file(options['file'])
        elif options['all']:
            self.load_all_files()
        else:
            self.stdout.write(
                self.style.ERROR('Укажите --file или --all')
            )

    def load_all_files(self):
        """Загрузка всех файлов shop*.yaml"""
        data_dir = os.path.join(settings.BASE_DIR, '..', 'data')
        
        if not os.path.exists(data_dir):
            self.stdout.write(
                self.style.ERROR(f'Папка {data_dir} не найдена')
            )
            return

        yaml_files = [f for f in os.listdir(data_dir) if f.startswith('shop') and f.endswith('.yaml')]
        
        if not yaml_files:
            self.stdout.write(
                self.style.WARNING('Файлы shop*.yaml не найдены')
            )
            return

        for filename in yaml_files:
            filepath = os.path.join(data_dir, filename)
            self.stdout.write(f'Загружаю {filename}...')
            self.load_file(filepath)

    def load_file(self, filepath):
        """Загрузка данных из одного YAML файла"""
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                data = yaml.safe_load(file)
            
            self.process_shop_data(data)
            self.stdout.write(
                self.style.SUCCESS(f'Данные из {filepath} успешно загружены')
            )
            
        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(f'Файл {filepath} не найден')
            )
        except yaml.YAMLError as e:
            self.stdout.write(
                self.style.ERROR(f'Ошибка парсинга YAML: {e}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Ошибка загрузки: {e}')
            )

    def process_shop_data(self, data):
        """Обработка данных магазина"""
        # Создаем или получаем магазин
        shop, created = Shop.objects.get_or_create(
            name=data['shop'],
            defaults={'is_accepting_orders': True}
        )
        
        if created:
            self.stdout.write(f'Создан магазин: {shop.name}')
        else:
            self.stdout.write(f'Обновляется магазин: {shop.name}')

        # Обрабатываем категории
        for category_data in data['categories']:
            category, created = Category.objects.get_or_create(
                id=category_data['id'],
                defaults={'name': category_data['name']}
            )
            category.shops.add(shop)
            
            if created:
                self.stdout.write(f'  Создана категория: {category.name}')

        # Удаляем старые товары этого магазина
        ProductInfo.objects.filter(shop=shop).delete()
        self.stdout.write(f'  Удалены старые товары магазина {shop.name}')

        # Обрабатываем товары
        products_count = 0
        for item in data['goods']:
            # Создаем или получаем продукт
            product, created = Product.objects.get_or_create(
                name=item['name'],
                defaults={'category_id': item['category']}
            )

            # Создаем информацию о продукте
            product_info = ProductInfo.objects.create(
                product=product,
                shop=shop,
                external_id=item['id'],
                model=item['model'],
                price=item['price'],
                price_rrc=item['price_rrc'],
                quantity=item['quantity']
            )

            # Обрабатываем параметры
            for param_name, param_value in item['parameters'].items():
                parameter, created = Parameter.objects.get_or_create(
                    name=param_name
                )
                
                ProductParameter.objects.create(
                    product_info=product_info,
                    parameter=parameter,
                    value=str(param_value)
                )

            products_count += 1

        self.stdout.write(f'  Загружено товаров: {products_count}')