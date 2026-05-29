#!/usr/bin/env python3
import json
import re
import urllib.request
from pathlib import Path

HTML_PATH = Path("Полётка.html")

API_URL = (
    "https://api.open-meteo.com/v1/forecast"
    "?latitude=55.7961"
    "&longitude=49.1088"
    "&daily=weather_code,temperature_2m_max,temperature_2m_min"
    "&timezone=Europe%2FMoscow"
    "&forecast_days=1"
)

WEATHER_CODE_RU = {
    0: "ясно",
    1: "преимущественно ясно",
    2: "переменная облачность",
    3: "пасмурно",
    45: "туман",
    48: "изморозь",
    51: "слабая морось",
    53: "морось",
    55: "сильная морось",
    56: "слабая ледяная морось",
    57: "ледяная морось",
    61: "слабый дождь",
    63: "дождь",
    65: "сильный дождь",
    66: "слабый ледяной дождь",
    67: "ледяной дождь",
    71: "слабый снег",
    73: "снег",
    75: "сильный снег",
    77: "снежная крупа",
    80: "слабые ливни",
    81: "ливни",
    82: "сильные ливни",
    85: "слабый снегопад",
    86: "сильный снегопад",
    95: "гроза",
    96: "гроза с градом",
    99: "сильная гроза с градом",
}


def celsius(v):
    n = int(round(float(v)))
    return f"+{n}" if n > 0 else str(n)


def fetch_weather():
    with urllib.request.urlopen(API_URL, timeout=20) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    daily = data["daily"]
    tmax = daily["temperature_2m_max"][0]
    tmin = daily["temperature_2m_min"][0]
    code = int(daily["weather_code"][0])

    desc = WEATHER_CODE_RU.get(code, "без осадков")
    main = f"Казань: днём до {celsius(tmax)}°C"
    sub = f"Сегодня: {desc}, утром {celsius(tmin)}°C"
    return main, sub


def replace_between_markers(text: str, start: str, end: str, value: str) -> str:
    pattern = re.compile(rf"({re.escape(start)})(.*?)({re.escape(end)})", flags=re.DOTALL)
    if not pattern.search(text):
        raise RuntimeError(f"Не найдены маркеры: {start} ... {end}")
    return pattern.sub(rf"\\1{value}\\3", text, count=1)


def update_html(main, sub):
    if not HTML_PATH.exists():
        raise FileNotFoundError(f"Файл не найден: {HTML_PATH}")

    text = HTML_PATH.read_text(encoding="utf-8")
    text = replace_between_markers(text, "<!-- WEATHER_MAIN_START -->", "<!-- WEATHER_MAIN_END -->", main)
    text = replace_between_markers(text, "<!-- WEATHER_SUB_START -->", "<!-- WEATHER_SUB_END -->", sub)
    HTML_PATH.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main, sub = fetch_weather()
    update_html(main, sub)
    print("OK")
    print(main)
    print(sub)
