import json
import os
from datetime import datetime
import re
import pandas as pd
import requests
import time
import urllib3
from bs4 import BeautifulSoup
from urllib.parse import urlparse



class MagnitApi:
    def __init__(self, phone, password, shop_code, burp_host='192.168.1.178', burp_port=8082):
        self.phone = phone
        self.password = password
        self.shop_code = shop_code
        self.burp_host = burp_host
        self.burp_port = burp_port
        self.proxies = {
            'http': f'http://{burp_host}:{burp_port}',
            'https': f'http://{burp_host}:{burp_port}'
        }

        self.base_headers = {
            'Host': 'middle-api.magnit.ru',
            'Content-Type': 'application/json',
            'X-Device-Platform': 'iOS',
            'Authorization': None,  # Будет установлен после авторизации
            'Baggage': 'sentry-environment=production,sentry-public_key=9f281c38318f79ef791f3d769012a4b6,sentry-release=ru.tander.magnit%408.58.0%2B97275,sentry-trace_id=29227cd2fe4c48c0b9b6e222d6eaee5f',
            'Accept': '*/*',
            'X-Platform-Version': '18.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'ru-RU;q=1.0, en-GB;q=0.9',
            'Sentry-Trace': '29227cd2fe4c48c0b9b6e222d6eaee5f-c658e89bac054f89-0',
            'User-Agent': 'Magnit/8.58.0 (ru.tander.magnit; build:97275; iOS 18.5.0) Alamofire/5.5.0',
            'X-Device-Id': '4605c218-7e2a-4d90-9064-4165682ca12d',
            'X-Device-Tag': 'F3890D93-E470-4471-BEA5-F3602F39F7F4_3BC81D3D-514D-4DAF-9DA8-B2E6B71FEA1A',
            'X-App-Version': '8.58.0',
            'Connection': 'keep-alive'
        }

        self.auth_token = None
        self.refresh_token = None
        self.authorize()

    def authorize(self):

        auth_url = "https://id.magnit.ru/connect/token"

        auth_headers = {
            'Host': 'id.magnit.ru',
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Device-Platform': 'iOS',
            'Accept': '*/*',
            'X-Platform-Version': '18.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'ru-RU;q=1.0, en-GB;q=0.9',
            'User-Agent': 'Magnit/8.58.0 (ru.tander.magnit; build:97275; iOS 18.5.0) Alamofire/5.5.0',
            'X-Device-Id': '4605c218-7e2a-4d90-9064-4165682ca12d',
            'X-Device-Tag': 'F3890D93-E470-4471-BEA5-F3602F39F7F4_3BC81D3D-514D-4DAF-9DA8-B2E6B71FEA1A',
            'X-App-Version': '8.58.0',
            'Connection': 'keep-alive'
        }

        auth_data = {
            'grant_type': 'password',
            'username': self.phone,
            'password': self.password,
            'client_id': 'mobile',
            'client_secret': 'secret',
            'scope': 'loyalty-mobile offline_access'
        }

        try:
            response = requests.post(
                auth_url,
                headers=auth_headers,
                data=auth_data,
                proxies=self.proxies,
                verify=False
            )

            if response.status_code == 200:
                auth_response = response.json()
                self.auth_token = auth_response.get('access_token')
                self.refresh_token = auth_response.get('refresh_token')
                self.base_headers['Authorization'] = f'Bearer {self.auth_token}'
                return True
            else:
                return False

        except Exception as e:
            print(f"Ошибка при авторизации: {e}")
            return False

    def handle_auth_error(self):
        if self.refresh_token:
            if self.refresh_auth_token():
                return True

        return self.authorize()

    def extract_brand_from_name(self, name):
        known_brands = [
            'Добрый', 'Черноголовка', 'Сады Придонья', 'Очаковский',
            'Моя цена', 'Adrenaline', 'Flash Up', 'Липецкая Росинка',
            'Evervess', 'Cool Cola', 'Любимый', 'Угличская', 'Il Primo',
            'Сок Я', 'Bona Aqua', 'Nar', 'Gorilla', 'Фрутмотив', 'Lipton',
            'Drive', 'А4', 'Нарзан', 'Red Bull', 'Rich', 'Chillout',
            'Moon Berry', 'Marmell', 'Frustyle', 'Святой источник',
            'J7', 'Ессентуки', 'Laimon Fresh', 'Borjomi', 'Barinoff',
            'Bionergy', 'Nabeghlavi', 'Donat Mg', 'Агуша', 'Aqua Minerale',
            'Теди', 'Chupa Chups', 'Tornado', 'Lit Energy', 'Сенежская',
            'Fancy', 'Bud', 'Пилигрим', 'Burn', 'Мохито', 'Fresh Bar', 'Street',
            'Volt', 'Псыж', 'Магнит', 'Архыз', 'Ах!', 'Балтика', 'Gorji',
            'Шишкин лес', 'Волчок', 'Lays', 'Dr Diesel', 'Рычал-Су',
            'Эконад', 'Cheetos', 'Кармадон', 'Hot Cat', 'Baikal',
            'Bio Nergy', 'J-7', 'Старорусская', 'Рушаночка',
            'X-Turbo', 'Вартемяжская', 'Piranhas Slam', 'By Баста',
            'Coca-Cola', 'Напитки из черноголовки', 'Chill King',
            'Naturelia', 'Нагутская', '5.0 Original', 'Мамина дача',
            'Мой', 'Black Wolf', 'Фрутоняня', 'Чудо-Ягода', 'Lucky Days',
            'Slasty Story', 'Кристальный родник', 'Напиток со вкусом лимона',
            'Фруктовый чай', 'Моя стихия', 'Ninja Star', 'Santo Stefano',
            'Эдельвейс', 'Роданика', 'Желтая бочка', 'Corona Cero',
            'Напиток фруктовый чай', 'Семейный секрет', 'Hoegaarden'
        ]

        for brand in known_brands:
            if brand.lower() in name.lower():
                return brand

        first_word = name.split()[0]
        return first_word if first_word not in ['Напиток', 'Вода', 'Сок'] else None

    def get_categories(self, shop_code):
        url = "https://magnit.ru/catalog/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cookie': f'nmg_dt=DELIVERY_TYPE_OFFLINE; shopCode={shop_code}; x_shop_type=STORE_TYPE_MM;',
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            catalog_divs = soup.find_all('div', class_='header-catalog-items')

            ids = []
            for div in catalog_divs:
                for a in div.find_all('a', href=True):
                    href = a['href']
                    if href.startswith('/catalog/'):
                        full_url = f"https://magnit.ru{href}"
                        path = urlparse(full_url).path
                        catalog_id = path.split('/catalog/')[-1].split('?')[0]
                        ids.append(catalog_id)

            return ids
        except Exception as e:
            return f"Произошла ошибка: {e}"

    def get_products(self, category_id, shop_code, page):
        url = f'https://magnit.ru/catalog/{category_id}?shopCode={shop_code}&page={page}'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Проверяем, что запрос прошел успешно
            soup = BeautifulSoup(response.text, 'html.parser')
            products = []

            # Находим все товары на странице
            product_divs = soup.find_all('div',
                                         class_='pl-stack-item pl-stack-item_size-6 pl-stack-item_size-4-m pl-stack-item_size-3-ml unit-catalog__stack-item')

            for product_div in product_divs:
                # Извлекаем цену по акции
                regular_price = product_div.find('div', class_='pl-text unit-catalog-product-preview-prices__regular')
                regular_price = regular_price.get_text(strip=True) if regular_price else None

                # Извлекаем цену без акции
                sale_price = product_div.find('div', class_='pl-text unit-catalog-product-preview-prices__sale')
                sale_price = sale_price.get_text(strip=True) if sale_price else None

                # Извлекаем название
                title = product_div.find('div', class_='pl-text unit-catalog-product-preview-title')
                title = title.get_text(strip=True) if title else None

                # Извлекаем рейтинг
                rating = product_div.find('div', class_='pl-text unit-catalog-product-preview-rating-score')
                rating = rating.get_text(strip=True) if rating else None

                # Извлекаем цену за вес
                unit_value = product_div.find('div', class_='pl-text unit-catalog-product-preview-unit-value')
                unit_value = unit_value.get_text(strip=True) if unit_value else None

                # Извлекаем вес
                weighted = product_div.find('div', class_='pl-text unit-catalog-product-preview-weighted')
                weighted = weighted.get_text(strip=True) if weighted else None

                # Проверяем, есть ли вес в названии
                weight_in_title = None
                if title:
                    # Регулярное выражение для поиска веса в названии
                    match = re.search(r'(\d+[\.,]?\d*)\s*(г|кг|грамм|килограмм|килограммов|граммов|мл|миллилитров|литров)', title,
                                      re.IGNORECASE)
                    if match:
                        weight_in_title = match.group(0)

                # Создаем словарь для текущего товара
                product_data = {
                    'title': title,
                    'regular_price': regular_price,
                    'sale_price': sale_price,
                    'rating': rating,
                    'unit_value': unit_value,
                    'weighted': weighted if weighted else weight_in_title,
                    'weight_in_title': weight_in_title,
                    'category': category_id
                }
                products.append(product_data)

            return products
        except Exception as e:
            print(f"Ошибка при получении данных: {str(e)}")
            return None

    def parse_products(self, shop_code, output, rpages):
        categories = self.get_categories(shop_code)
        all_products = []

        for category_id in categories:
            for page in range(rpages):
                products = self.get_products(category_id, shop_code, page)
                if products:
                    all_products.extend(products)

        # Сохраняем все продукты в JSON файл
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(all_products, f, ensure_ascii=False, indent=4)

        return all_products
