import yaml
from django.core.management.base import BaseCommand
from backend.models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter


class Command(BaseCommand):
    help = 'Загрузка данных из YAML файла'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Путь к YAML файлу')

    def handle(self, *args, **options):
        file_path = options['file_path']
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = yaml.safe_load(file)
            
            # Создаем магазин
            shop, created = Shop.objects.get_or_create(
                name=data['shop'],
                defaults={'is_accepting_orders': True}
            )
            if created:
                self.stdout.write(f'Создан магазин: {shop.name}')
            
            # Создаем категории
            for category_data in data['categories']:
                category, created = Category.objects.get_or_create(
                    id=category_data['id'],
                    defaults={'name': category_data['name']}
                )
                category.shops.add(shop)
                if created:
                    self.stdout.write(f'Создана категория: {category.name}')
            
            # Удаляем старые товары магазина
            ProductInfo.objects.filter(shop=shop).delete()
            
            # Создаем товары
            for item in data['goods']:
                # Создаем продукт
                product, created = Product.objects.get_or_create(
                    name=item['name'],
                    category_id=item['category']
                )
                
                # Создаем информацию о продукте
                product_info = ProductInfo.objects.create(
                    product=product,
                    external_id=item['id'],
                    model=item['model'],
                    price=item['price'],
                    price_rrc=item['price_rrc'],
                    quantity=item['quantity'],
                    shop=shop
                )
                
                # Создаем параметры
                for name, value in item['parameters'].items():
                    parameter, _ = Parameter.objects.get_or_create(name=name)
                    ProductParameter.objects.create(
                        product_info=product_info,
                        parameter=parameter,
                        value=value
                    )
                
                self.stdout.write(f'Загружен товар: {product.name}')
            
            self.stdout.write(
                self.style.SUCCESS(f'Данные успешно загружены из {file_path}')
            )
            
        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(f'Файл {file_path} не найден')
            )
        except yaml.YAMLError as e:
            self.stdout.write(
                self.style.ERROR(f'Ошибка парсинга YAML: {e}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Ошибка загрузки данных: {e}')
            )