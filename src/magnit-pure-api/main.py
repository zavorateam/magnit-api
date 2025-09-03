import json
import os
from datetime import datetime
import re
import pandas as pd
import requests
import time
import urllib3


class MagnitParser:
    def __init__(self, phone, password, burp_host='192.168.1.178', burp_port=8082):
        self.phone = phone
        self.password = password
        self.burp_host = burp_host
        self.burp_port = burp_port
        self.proxies = {
            'http': f'http://{burp_host}:{burp_port}',
            'https': f'http://{burp_host}:{burp_port}'
        }

        self.request_signs = {
            'moscow': {
                0: '138fe42af0cbec501aa462b05c7a99d08fbac20ac53997434cec426ce5b7e383dcb673001f8f602c0e53d7d0709d802462afdf091affb5166d576ba1bb200975',
                20: 'fda8593ffdd7fd82856f8142262fb6f07c36a3a17846d02f6d8c9ff02040372fb9aae5cb41c32491dd02b416aa697d06414a4ce9efb58bf87928f4869be266a6',
                40: 'b50cf209d8ff344337fad1d8946b44a37e6f21d4bcaba61f3703fd1d4261a7cb258a91d27dce91de291a4bf36be74bc17877a7de54ba141fbe1a191fb19d226b',
                60: 'ff55b631f4af72b9eb6693a8b2c9fca210d70dc1391fe9ffb22d6e7ec46270eb2daf2d0adb79ced7c19af686350c16ff834b5bb9722077f4e6b12b21e0c601d0',
                80: 'd15450d0e4cb6532bc378c0664967985f66f43f87cfb5d8e1bbd94d0db78e9fd01708eebfd24c1a6372bdfe5d0af909f67457b5b993e964cb40b05e93953d6d5',
                100: 'e370c6f2779fc215fbbb22c61131ae5bd82d7798e97a93255bba4b84dc57ec94dd3bdc9c7608a2c0762673dcf8dd3fb79dc4040749e5854098ce8f8736ba7702',
                120: '23d35afd2e6a7db1452af691671513096110d69591b46844fb9358a454f511d1c2b72ed815d2f61f1b695db14f94108f01ab2721d8b394d661365581550a3309',
                140: 'e618bd0b3d84e49be27c62ff4da0f6c5e4422c302aa4ea94d8b6bf9f761a319a75b5ec41a17022e17970b99a8b91febde77ad4b8618953549bb141e0efb7c7a3',
                160: '95fb90ed00efa20e88894d3a88177291416de945fab137f89378121f1d8abae06ee377bfddc177b31e21aee9b5f2d4e0729985791610e0c5e2d600c4e5c5a715',
                180: 'b1997f7c8e3c6b750c117813e78d8b510215076e215aef50036b0aa5b8bc8c57207a7fabbd862fca1a0c80a5a36f26be83850738945918c9b9e314405a970549',
                200: 'ce528bc989428d813783a73f5848d8d08135aec7afa975380db5b002a9f01136776f4ba2a5819f81bf069ae960c470c80350e364ee4946e3d2674a81d2bfb2e8',
                220: 'e3b9805db76464e52eff40e03c8f8cd0fbf5cb9b96a1683b7e7864a0122d8563806d9e063cc1a30f56e182ca836464075bc72af28f53b884d23303cbe5037dff',
                240: 'a8d65fa4f45898f368291a7379f2b8aa6a15ed6f9a4b0526f6af1013e56a0917746b2902b7c9b91bdba6eb2d67d574694b15b278a4779323f9f0f91dc78e1920',
                260: 'edb0952ae465fa82d6ba333989a28e0c36866427608337d5e8106b62a52750ff27a3afd847e7715cb9a04cd42bc636f34d98d7b9bc38fada114d60f6222508d2'
            },
            'spb': {
                0: '310f5c82602c5e7e639dc3de64d602900af01fa05ff5bd92fcef81cd3e54ade0d6bdb757cc7bfeb1da6f1b0d9c1b45acb8f801d61b2a00099c8fbb444860367c',
                20: 'e0c41c5ca84e1fcd7991817d74558fdf5efbe81764b74475ba0e4fe4e890617bb3ab147eb0daf02f7cd99a57d925bbe1c6daa1eda90ec9d69e302dd00f3409b8',
                40: '4dc12191d9dfe4e3a9e5a6e3aa344c746f582504da53385787b9c4ef19cabe08a7ddbf8654afa3f0f28b99c749ecaadc7027d64303334a587c1baeb9178cee29',
                60: '57fa4d62155dbfc6b327d28e48af1b7c3c71ab52625df4f90b35f15fb9fe1cd59f94607319ba4fc36368964cc85cbe1588f406a70ac7eb0d1f68f10fcdf02414',
                80: 'e172e44f070ab6b3dcaec3598d6345b55a31f0b7b9b91824e23665b258873f24d773e03dff26f88b26ecda3190f7226b67f4928761964d32c81e7d5ff26ca1e5',
                100: 'b2d85b6ce98c1a70c8d95023c25d9e85cf1169bc90ad3005817c61fd88a56c8ceae8d92545e9946223831f769d216de05035bef12255a30b074301fe136af5a6',
                120: '05560bba2004649b897c636ee991a3eadbb09fe639f86d24fd38e63bd12ada9635e421af4c1c46e2a7b15ac44788387aec83494fb40be3da5793b4d33d810919',
                140: '1dd048b75f1bce05fc40a4bab4b55ff211cfafcdcf15b8574a45adf6b3b34b24d818e4ba976b3cba41350235d61c925601bd77e845498703d5ed50e8c7b9bd46',
                160: 'cb55200c713946153c152f522d7f5a2dc033da30b7c72527082690d24a234bb50dcb346b6a2cfefd76c3384bccf845e3296ebee20f50181e8939bd1f4f6d3f29',
                180: 'bc4849fa2403d05963d76faa3b585c2eac1121c4bb1a2f5989a92f8629aadccd6ae0c5c1aa6d36886b6f7bee2f5768e1e7070adc7f9ff684b8ffa134ddd6dd9b',
                200: 'a1d2004836ed81862c37d37b5f26b3572f6a238ccfde0f38a8acf612e78cd01579f13f90c8191165a5b11d4860f8d197d75abd22cc9ac29ff1e16d1b0ac0c89e',
                220: '77ef3a53c7d5b6125af03b71074b20fc32e00e2a69cf4a20b870b20d11e9100dd065b1a89e5cac52630d43371bca7778551827f8876b83f738434bc8722a244f',
                240: '972937885c09b24388f1ed07cd8fb8169c8bc1938227a84593ab9931a10ff7df69455cf97689be964b1f83a2d8b4aeabfc80c67edb369c50b7d89d161c43119d',
                260: '4687e8be597ce34f1dc4d7d9d5ae82cde3a4b650695bf20cd2d40003f62a97216db46627d7d208b90e5e2aee6d7219d0178f945cb1e9861816611e35764f9fee',
                280: '67a9953f8f55cee1fc91788511d65a4639a2dd6b235e2e077e66479fa6ade5696ee015fe9f669cb4b21172e7cb1b7fa7f946e0338c25b33fb1e7b777d1feecf8',
                300: '2ff2449547ad07e57a95b01c43168bae93c2923dbe2bc58f043f343335d414fb51f4932598064e1deb1212bdd5ab92cebcb047e70850b53f59b187990c2130e9',
                320: 'e2e13b6e568cf969aa7246d731eb59ac44581348b5913258e94a972f55543933fd441f42ec55da6ff085ddf841e2e32d5f4d9f0db6a22e93c46ec1406a336251'
            }
        }

        self.store_codes = {
            'moscow': '777885',
            'spb': '699422'
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

        os.makedirs('output', exist_ok=True)

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

    def get_products(self, category_id, city, offset=0, limit=20):
        url = 'https://middle-api.magnit.ru/v2/goods/search'

        payload = {
            "storeCode": self.store_codes[city],
            "storeType": "1",
            "cityId": "1",
            "categories": [int(category_id)],
            "catalogType": "1",
            "includeAdultGoods": True,
            "pagination": {
                "offset": offset,
                "limit": limit
            },
            "sort": {
                "order": "desc",
                "type": "popularity"
            }
        }

        try:

            payload_str = json.dumps(payload, ensure_ascii=False, separators=(',', ':'))

            request_sign = self.request_signs[city].get(offset)
            if request_sign is None:
                print(f"Предупреждение: нет подписи для offset={offset} для города {city}, пропускаем запрос")
                return None

            headers = self.base_headers.copy()
            headers['X-Request-Sign'] = request_sign
            headers['Content-Length'] = str(len(payload_str.encode('utf-8')))

            if offset > 0:
                print("Ожидание перед следующим запросом...")
                time.sleep(3)

            response = requests.post(
                url,
                data=payload_str,
                headers=headers,
                proxies=self.proxies,
                verify=False
            )

            print(f"Статус ответа: {response.status_code}")

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 403:
                print(f"Ошибка доступа: {response.text}")
                if "Access denied" in response.text:
                    print("Возможно, истек токен авторизации")
                    if self.handle_auth_error():
                        return self.get_products(category_id, city, offset, limit)
                return None
            else:
                print(f"Ошибка при запросе: {response.text}")
                return None

        except Exception as e:
            print(f"Ошибка при получении данных: {str(e)}")
            return None

    def parse_products(self, category_id, city):
        print(f"\nНачинаю парсинг товаров для категории {category_id} в городе {city}...")

        all_products = []
        offset = 0
        limit = 20

        while True:
            try:
                response_data = self.get_products(category_id, city, offset, limit)

                if not response_data:
                    print("Ошибка получения данных")
                    break

                if 'items' not in response_data:
                    print("Ошибка: В ответе нет поля 'items'")
                    print(f"Структура ответа: {list(response_data.keys())}")
                    break

                products = response_data['items']
                if not products:
                    print("Больше товаров нет")
                    break

                print(f"Получено товаров (offset={offset}): {len(products)}")

                for product in products:
                    regular_price = product.get('price')
                    promo_price = None

                    promotion = product.get('promotion', {})
                    if promotion.get('isPromotion', False) and promotion.get('oldPrice') is not None:
                        promo_price = regular_price
                        regular_price = promotion.get('oldPrice')

                    if regular_price is not None:
                        regular_price = regular_price / 100
                    if promo_price is not None:
                        promo_price = promo_price / 100

                    name = product.get('name')
                    brand = self.extract_brand_from_name(name) if name else None

                    processed_product = {
                        'id': product.get('id'),
                        'name': name,
                        'brand': brand,
                        'regular_price': regular_price,
                        'promo_price': promo_price
                    }
                    all_products.append(processed_product)

                pagination = response_data.get('pagination', {})
                if not pagination.get('hasMore', False):
                    print("Достигнут конец списка")
                    break

                offset += limit
                time.sleep(1)

            except Exception as e:
                print(f"Ошибка при обработке страницы (offset={offset}): {str(e)}")
                import traceback
                print("Детали ошибки:")
                print(traceback.format_exc())
                break

        if all_products:
            print(f"\nНачинаю сохранение {len(all_products)} товаров...")
            try:
                df = pd.DataFrame(all_products)

                df['regular_price'] = df['regular_price'].apply(lambda x: f'{x:.2f}' if pd.notnull(x) else '')
                df['promo_price'] = df['promo_price'].apply(lambda x: f'{x:.2f}' if pd.notnull(x) else '')

                df.columns = ['ID товара', 'Наименование', 'Бренд', 'Регулярная цена', 'Промо цена']

                output_file = f'output/magnit_products_{city}.xlsx'

                df.to_excel(output_file, index=False, engine='openpyxl')

                print(f"\nУспешно обработано товаров: {len(all_products)}")
                print(f"Результаты сохранены в файл: {output_file}")
            except Exception as e:
                print(f"Ошибка при сохранении результатов: {str(e)}")
                import traceback
                print("Детали ошибки:")
                print(traceback.format_exc())
        else:
            print("\nНет данных для сохранения")


if __name__ == "__main__":
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    parser = MagnitParser('+79001234567', 'password')
    category_id = 4874

    print("\nПарсинг товаров для Москвы")
    parser.parse_products(category_id, 'moscow')

    print("\nПарсинг товаров для Санкт-Петербурга")
    parser.parse_products(category_id, 'spb')