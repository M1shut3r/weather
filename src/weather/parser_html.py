import json
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator

# Путь вычисляется от файла модуля — работает из любой директории запуска
HEADERS_FILE = Path(__file__).parent / "data" / "http_headers.json"
BASE_URL = "https://world-weather.ru/pogoda/russia/{city}/"
IP_API_URL = "https://api.2ip.io/"
REQUEST_TIMEOUT = 10


def load_headers() -> dict:
    """Загрузка заголовков из JSON-файла."""
    with HEADERS_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def html_parser(mas_days_html):
    """Парсинг дней недели из html."""
    json_info_days = []
    for day in mas_days_html:
        json_day = {}
        for item in day:
            name_class = item.attrs
            json_day[name_class["class"][0]] = item.contents[0]
        json_info_days.append(json_day)
    return json_info_days


def weather_parser(mas_weather):
    """Парсинг вида погоды."""
    json_info_weather = []
    for day in mas_weather:
        json_info_weather.append(day)
    return json_info_weather


def parser(city: str):
    """Возвращает (данные по дням, описания погоды) для города."""
    headers = load_headers()
    translator = GoogleTranslator(source="ru", target="en")
    translation_city = translator.translate(city)
    url = BASE_URL.format(city=translation_city.lower())

    page = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
    page.raise_for_status()
    content_weather = page.content

    soup = BeautifulSoup(content_weather, "html.parser")
    mas_days_div = [
        item.find_all("div") for item in soup.find_all("li", class_="tab-w")
    ]
    spans = soup.find_all("span", class_="icon-weather")
    mas_weather_span = [span.get("title") for span in spans]

    return html_parser(mas_days_html=mas_days_div), weather_parser(
        mas_weather=mas_weather_span
    )


def find_your_city(api_token: str) -> str:
    """Получение местоположения пользователя с помощью 2ip.io."""
    response = requests.get(
        IP_API_URL,
        params={"token": api_token, "lang": "ru"},
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    response_json = response.json()
    return response_json["city"]
