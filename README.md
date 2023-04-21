# Продуктовый помощник Foodgram

### Описание проекта:
Приложение «Продуктовый помощник Foodgram»: сайт, на котором пользователи будут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Сервис «Список покупок» позволит пользователям создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

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
Также проект доступен по адресу:

```
http://158.160.10.230/
```

![Workflow Status Badge](https://github.com/ApriCotBrain/foodgram-project-react/actions/workflows/workflow.yml/badge.svg)
