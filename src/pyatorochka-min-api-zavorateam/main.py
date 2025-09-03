import json
import requests

class PyatorochkaMinApi:
    def __init__(self):
        self.base_url_categories = "https://5d.5ka.ru/api/catalog/v2/stores/35XY/categories"
        self.base_url_products = "https://5d.5ka.ru/api/catalog/v2/stores/35XY/categories/{category_id}/products"
        self.categories = []
        self.products = []

    def fetch_categories(self):
        """Загружает данные о категориях из API."""
        params = {
            'mode': 'delivery',
            'include_subcategories': 1,
            'include_restrict': True
        }
        response = requests.get(self.base_url_categories, params=params)
        if response.status_code == 200:
            self.categories = extract_categories(response.json())
        else:
            raise Exception(f"Failed to fetch categories: {response.status_code}")

    def fetch_products(self, category_id):
        """Загружает данные о продуктах для заданной категории из API."""
        params = {
            'mode': 'delivery',
            'include_restrict': True,
            'limit': 12
        }
        url = self.base_url_products.format(category_id=category_id)
        response = requests.get(url, params=params)
        if response.status_code == 200:
            self.products = extract_products(response.json())
        else:
            raise Exception(f"Failed to fetch products: {response.status_code}")

    def get_categories(self):
        """Возвращает список всех категорий и их подкатегорий."""
        if not self.categories:
            self.fetch_categories()
        return self.categories

    def get_products(self, category_id):
        """Возвращает список продуктов для заданной категории."""
        self.fetch_products(category_id)
        return self.products

    def get_discounted_products(self):
        """Возвращает список продуктов со скидкой."""
        discounted_products = []
        for product in self.products:
            if product['prices'].get('discount') is not None:
                discounted_products.append(product)
        return discounted_products

    def get_filters_for_category(self, category_id):
        """Возвращает список фильтров для заданной категории."""
        for category in self.categories:
            if category['id'] == category_id:
                return category.get('filters', [])
        return []

    def get_product_by_plu(self, plu):
        """Возвращает информацию о продукте по его PLU."""
        for product in self.products:
            if product['plu'] == plu:
                return product
        return None

def extract_categories(categories_data):
    categories_info = []

    def parse_category(category):
        category_info = {
            'id': category.get('id'),
            'name': category.get('name'),
            'image_link': category.get('image_link'),
            'filters': category.get('filters', []),
            'children': []
        }

        if 'children' in category:
            for child in category['children']:
                category_info['children'].append(parse_category(child))

        return category_info

    for category in categories_data:
        categories_info.append(parse_category(category))

    return categories_info

def extract_products(products_data):
    products_info = []

    for product in products_data.get('products', []):
        product_info = {
            'plu': product.get('plu'),
            'name': product.get('name'),
            'image_links': product.get('image_links'),
            'prices': product.get('prices'),
            'stock_limit': product.get('stock_limit'),
            'category_id': products_data.get('id')
        }
        products_info.append(product_info)

    return products_info

# Пример использования
# api = PetyorochkaAPI()
# categories = api.get_categories()
# products = api.get_products('251C12946')
# discounted_products = api.get_discounted_products()
