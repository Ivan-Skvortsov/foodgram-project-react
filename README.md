<div id="top"></div>
<div align="center">
<h1>Проект «Продуктовый помощник»</h1>
  <h3>
    Дипломный проект курса Python разработчик+<br />
  </h3>
    <h6>(версия 1.0 - без инфраструктуры)</h6>
    <br />
</div>

## О проекте
Проект реализует сервис, на котором пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд
<p align="right">(<a href="#top">наверх</a>)</p>

## Использованные технологии
* [Django](https://www.djangoproject.com/)
* [Django REST framework](https://www.django-rest-framework.org/)
* [Djoser](https://djoser.readthedocs.io/en/latest/getting_started.html)
<p align="right">(<a href="#top">наверх</a>)</p>

## Запуск проекта

Склонируйте проект на Ваш компьютер
   ```sh
   git clone https://github.com/Ivan-Skvortsov/foodgram-project-react.git
   ```
Перейдите в папку с проектом
   ```sh
   cd foodgram-project-react
   ```
Активируйте виртуальное окружение
   ```sh
   python3 -m venv venv
   ```
   ```sh
   source venv/bin/activate
   ```
Обновите менеджер пакетов (pip)
   ```sh
   pip3 install --upgrade pip
   ```
Установите необходимые зависимости
   ```sh
   pip3 install -r requirements.txt
   ```
Перейдите в папку с бэкенд проекта
   ```sh
   cd backend
   ```
Выполните миграции
   ```sh
   python3 manage.py makemigrations
   ```
   ```sh
   python3 manage.py migrate
   ```
Создайте пользователя с правами администратора
   ```sh
   python3 manage.py createsuperuser
   ```
Запустите проект локально
   ```sh
   python3 manage.py runserver
   ```
Проект запустится на адресе http://127.0.0.1

Увидеть спецификацию API вы сможете по адресу http://127.0.0.1/api/docs/redoc.html

Панекль администрирования доступна по адресу http://127.0.0.1/admin/

<p align="right">(<a href="#top">наверх</a>)</p>

## Об авторе
Автор проекта: Иван Скворцов<br/><br />
[![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Ivan-Skvortsov/)
[![Gmail](https://img.shields.io/badge/Gmail-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:pprofcheg@gmail.com)
[![Telegram](https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/Profcheg)
<p align="right">(<a href="#top">наверх</a>)</p>
