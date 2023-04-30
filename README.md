# Продуктовый помощник Foodgram

### Описание проекта:
Cайт Foodgram, «Продуктовый помощник». Онлайн-сервис и API для него. На этом сервисе пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

### Технологии:
- Django 3.2.7
- djangorestframework 3.14.0
- Pillow 9.4.0
- django-import-export 3.1.0
- djoser 2.1.0
- django-filter 23.1
- django-cors-headers 3.14.0
- python-dotenv
- gunicorn 20.0.4
- psycopg2-binary 2.8.6

### Как запустить проект:
Клонируйте репозиторий, перейдите в директорию с проектом:

```
git@github.com:ApriCotBrain/foodgram-project-react.git
```

В директории infra/ создайте файл .env по примеру example.env

Запустите контейнеры:

```
docker-compose up -d --build
```

Выполните по очереди команды:

```
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
docker-compose exec backend python manage.py collectstatic --no-input
```

Проект доступен по адресу:

```
http://localhost/
```
После запуска проекта документация доступна по адресу:

```
http://localhost/api/docs/
```

![Workflow Status Badge](https://github.com/ApriCotBrain/foodgram-project-react/actions/workflows/workflow.yml/badge.svg)
