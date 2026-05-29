# Poletka Weather Auto Update

Этот проект обновляет текст прогноза в `Полётка.html` 1 раз в день через GitHub Actions.

## Что обновляется

Скрипт меняет только блоки между маркерами:

- `<!-- WEATHER_MAIN_START --> ... <!-- WEATHER_MAIN_END -->`
- `<!-- WEATHER_SUB_START --> ... <!-- WEATHER_SUB_END -->`

## Запуск локально

```bash
python3 scripts/update_weather_poletka.py
```

## Расписание в GitHub Actions

Файл: `.github/workflows/weather.yml`

- ежедневно в `04:00 UTC` (`07:00 МСК`)
- можно запустить вручную через `Run workflow`
