#!/usr/bin/env python3
import json
import re
import urllib.request
from pathlib import Path

HTML_CANDIDATES = [
    Path("Полётка.html"),
    Path("Полётка.html"),
]

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


def resolve_html_path() -> Path:
    for p in HTML_CANDIDATES:
        if p.exists():
            return p

    for p in Path(".").glob("*.html"):
        text = p.read_text(encoding="utf-8")
        if "<!-- WEATHER_MAIN_START -->" in text and "<!-- WEATHER_SUB_START -->" in text:
            return p

    raise FileNotFoundError("Не найден HTML-файл с маркерами WEATHER_*")


def fetch_weather():
    try:
        with urllib.request.urlopen(API_URL, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"WARN: не удалось получить погоду ({e}), оставляю текущий текст без изменений")
        return None, None

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
    return pattern.sub(lambda m: f"{m.group(1)}{value}{m.group(3)}", text, count=1)


def update_html(html_path: Path, main, sub):
    text = html_path.read_text(encoding="utf-8")
    text = replace_between_markers(text, "<!-- WEATHER_MAIN_START -->", "<!-- WEATHER_MAIN_END -->", main)
    text = replace_between_markers(text, "<!-- WEATHER_SUB_START -->", "<!-- WEATHER_SUB_END -->", sub)
    html_path.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    html_path = resolve_html_path()
    main, sub = fetch_weather()
    if not main or not sub:
        print("OK (no update)")
        raise SystemExit(0)

    update_html(html_path, main, sub)
    print("OK")
    print(f"file: {html_path}")
    print(main)
    print(sub)
