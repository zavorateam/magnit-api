# Magnit Pure API

**Magnit Pure API** — это Python-библиотека для работы с API и веб-ресурсами сети магазинов "Магнит". Она позволяет получать информацию о категориях и товарах, а также авторизовываться в системе.

---

## Установка

### Требования

* Python 3.9+
* Установленные зависимости (см. ниже)

### Установка через pip

```bash
pip install pyatorochka-min-api
```

или вручную:

```bash
git clone https://github.com/ваш-репозиторий/magnit-pure-api.git
cd magnit-pure-api
pip install -r requirements.txt
```

### Зависимости

```
requests>=2.31.0
beautifulsoup4>=4.12.2
pandas>=2.0.0
urllib3>=2.0.0
```

---

## Быстрый старт

### Инициализация

```python
from magnit_api import MagnitApi

# Инициализация с указанием телефона, пароля и кода магазина
# Параметры burp_host и burp_port не используются в текущей версии
api = MagnitApi(
    phone="+79991234567",
    password="your_password",
    shop_code="12345"
)
```

---

## Основные методы

### 1. Авторизация

```python
if api.authorize():
    print("Авторизация успешна!")
else:
    print("Ошибка авторизации.")
```

### 2. Получение списка категорий

```python
categories = api.get_categories(shop_code="12345")
print(categories)
```

### 3. Получение товаров по категории

```python
products = api.get_products(
    category_id="4226-molochnye-produkty", # у вас будет свой
    shop_code="12345",
    page=4
)
for product in products:
    print(product['title'], product['sale_price'])
```

### 4. Парсинг всех товаров и сохранение в JSON

```python
api.parse_products(
    shop_code="12345",
    output="products.json",
    rpages=2  # количество страниц товаров для парсинга
)
```

---

## Примеры использования

### Пример 1: Получение всех категорий и товаров

```python
api = MagnitApi(phone="+79991234567", password="your_password", shop_code="12345")
categories = api.get_categories("12345")
for category in categories:
    products = api.get_products(category, "12345", 1)
    print(f"Категория: {category}, Товаров: {len(products)}")
```

### Пример 2: Сохранение данных в CSV

```python
import pandas as pd

api = MagnitApi(phone="+79991234567", password="your_password", shop_code="12345")
products = api.parse_products("12345", "products.json", 2)
df = pd.DataFrame(products)
df.to_csv("products.csv", index=False)
```

---

## Обработка ошибок

* Если авторизация не удалась, проверьте правильность телефона/пароля.
* Если не удается получить данные, проверьте код магазина и интернет-соединение.
* В текущей версии \*\*Burp\*\* прокси \*\*не используется\*\*