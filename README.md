# YaTube

[![coverage](https://img.shields.io/codecov/c/github/ThatCoderMan/hw05_final.svg)](https://app.codecov.io/gh/ThatCoderMan/hw05_final)
[![workflows](https://github.com/yandex-praktikum/hw05_final/actions/workflows/python-app.yml/badge.svg?branch=master)](https://github.com/yandex-praktikum/hw05_final/actions/workflows/python-app.yml)


<details>
<summary>Project stack</summary>

- Python 3.7
- Django 2.2
- Pillow
- Pytest

</details>

### Описание:

Сайт "YaTube" - это онлайн-сервис для публикации,
получения записей, комментирования записей других пльзователей и
подписки на авторов.

### Инструкция по запуску:
Клонируйте репозиторий:
```commandline
git clone git@github.com:ThatCoderMan/hw05_final.git
```
Установите и активируйте виртуальное окружение:

- *для MacOS:*
    ```commandline
    python3 -m venv venv
    ```
- *для Windows:*
    ```commandline
    python -m venv venv
    source venv/bin/activate
    source venv/Scripts/activate
    ```
Установите зависимости из файла requirements.txt:
```commandline
pip install -r requirements.txt
```
Примените миграции:
```commandline
python manage.py migrate
```
В папке с файлом manage.py выполните команду для запуска сервера:
```commandline
python manage.py runserver
```

### Автор проекта:

[Artemii Berezin](https://github.com/ThatCoderMan)
