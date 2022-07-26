<div id="top"></div>
<div align="center">
<h1>Проект «Продуктовый помощник»</h1>
</div>

## О проекте
В рамках проекта реализован бэкенд и инфраструктура сервиса, на котором пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд
<p align="right">(<a href="#top">наверх</a>)</p>

## Использованные технологии и пакеты
* [Django](https://www.djangoproject.com/)
* [Django REST framework](https://www.django-rest-framework.org/)
* [Django-filter](https://django-filter.readthedocs.io/en/stable/guide/usage.html)
* [Djoser](https://djoser.readthedocs.io/en/latest/getting_started.html)
* [Docker](https://www.docker.com/)
* [GitHub Actions](https://github.com/features/actions)
<p align="right">(<a href="#top">наверх</a>)</p>

## Необходимый софт
Для развертывания проекта потребуется машина с предустановленным Docker и Docker-Compose.<br/>
Инструкцию по установке можно найти на <a href="https://docs.docker.com/">официальном сайте</a>.

## Установка
Склонируйте проект на Ваш компьютер
   ```sh
   git clone https://github.com/Ivan-Skvortsov/foodgram-project-react.git
   ```
Перейдите в папку с инструкциями docker-compose
   ```sh
   cd foodgram-project-react/infra
   ```
Создайте файл с переменными окружения
   ```sh
   touch .env
   ```
Наполните файл следующими переменными
   ```sh
   SECRET_KEY  # секректный ключ Django
   DB_ENGINE  # используемая база данных (django.db.backends.postgresql_psycopg2)
   DB_NAME  # имя базы данных
   POSTGRES_USER  # имя пользователя базы данных
   POSTGRES_PASSWORD  # пароль пользователя базы данных
   DB_HOST  # адрес хоста, на котором будет запущена база данных
   DB_PORT  # порт хоста, на котором будет запущена база данных
   ```
Запустите контейнеры
   ```sh
   sudo docker-compose up -d
   ```
Создайте суперпользователя django
   ```sh
   sudo docker-compose exec backend python3 manage.py createsuperuser
   ```
Для развертывания проекта на сервере, необходимо добавить доменное имя сервера в перечень разрешенных хостов Django (backend/backend/settings.py)


## Об авторе
Автор проекта: Иван Скворцов<br/><br />
[![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Ivan-Skvortsov/)
[![Gmail](https://img.shields.io/badge/Gmail-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:pprofcheg@gmail.com)
[![Telegram](https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/Profcheg)
<p align="right">(<a href="#top">наверх</a>)</p>
