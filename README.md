# Magnit API Parser

Парсер товаров из API магазинов "Магнит" с сохранением в Excel.

## Функционал
- Авторизация в API Magnit (OAuth 2.0)
- Парсинг товаров с пагинацией
- Извлечение брендов из названий
- Обработка промо-цен
- Экспорт в Excel

## Технологии
- Python 3.9+
- Библиотеки: `requests`, `pandas`, `urllib3`

## Установка
```bash
pip install -r requirements.txt