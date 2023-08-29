# Foodgram
Адрес сайта: https://foodgramou.myvnc.com

Логин администратора(эл.почта): 
```
admin@admin.ad
```

Пароль администратора: 
```
vasya
```
## Описание

Foodgram - это [сайт](https://foodgramou.myvnc.com), на котором пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Пользователям сайта доступен сервис «Список покупок», который позволяет создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

## Используемые технологии
* [Python](https://www.python.org/downloads/release/python-3114/),
* [Django](https://docs.djangoproject.com/en/4.2/releases/4.2.4/),
* [Django REST Framework 3.14.](https://www.django-rest-framework.org/community/release-notes/#3140),
* [Djoser](https://djoser.readthedocs.io/en/latest/getting_started.html),
* [PostgreSQL](https://www.postgresql.org/docs/13/release-13-10.html),
* [React](https://github.com/facebook/react/blob/main/CHANGELOG.md#1702-march-22-2021),
* [Gunicorn](https://docs.gunicorn.org/en/20.1.0/),
* [Nginx](https://nginx.org/ru/docs/),
* [Docker](https://www.docker.com/products/docker-desktop/),
* [GitHub Actions](https://docs.github.com/en/actions)

## Как запустить проект локально
1. Клонируйте репозиторий и перейдите в него в командной строке:
```bash
git clone git@github.com:Olga-Ustinova/foodgram-project-react.git

cd foodgram-project-react
```
2. Перейдите в директорию `backend`, создайте и активируйте виртуальное окружение, установите зависимости из файла `requirements.txt` и выполните миграции:
```bash
cd backend
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
python manage.py migrate
```
3. В папке `infra/` создайте файл `.env` и заполните его своими данными. Все необходимые переменные перечислены в файле `.env.example`.
4. Собрерите и запустите докер-контейнеры через Docker Compose:
```bash
docker compose up --build
```

## Как развернуть проект на сервере
1. Подключитесь к удаленному серверу и создайте на сервере директорию `foodgram`:
```bash
ssh -i путь_до_файла_с_SSH_ключом/название_файла_с_SSH_ключом_без_расширения login@ip
mkdir foodgram
```
2. Установите Docker Compose на сервер:
```bash
sudo apt update
sudo apt install curl
curl -fSL https://get.docker.com -o get-docker.sh
sudo sh ./get-docker.sh
sudo apt-get install docker-compose-plugin
```
3. Скопируйте файлы `docker-compose.production.yml` и `.env` в директорию `foodgram/` на сервере:
```bash
scp -i path_to_SSH/SSH_name docker-compose.production.yml \
    username@server_ip:/home/username/taski/docker-compose.production.yml
```
где:
* `path_to_SSH` - путь к файлу с SSH-ключом;
* `SSH_name` - имя файла с SSH-ключом (без расширения);
* `username` - ваше имя пользователя на сервере;
* `server_ip` - IP вашего сервера.
4. Запустите Docker Compose в режиме демона:
```bash
sudo docker compose -f docker-compose.production.yml up -d
```
5. Выполните миграции, соберите статические файлы бэкенда и скопируйте их в `/backend_static/static/`:
```bash
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /backend_static/static/
```
6. Откройте конфигурационный файл `Nginx` в редакторе `nano`:
```bash
nano /etc/nginx/sites-enabled/default
```
7. Измените настройки в nginx с перенаправлением запросов на порт 10000:
```bash
server {
    server_name <...>;
    server_tokens off;

    location / {
        proxy_pass http://127.0.0.1:10000;
    }
}
```
8. Проверьте правильность конфигурации `Nginx`:
```bash
sudo nginx -t
```
Если вы получаете следующий ответ, значит, ошибок нет:
```bash
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
```
9. Перезапустите `Nginx`:
```bash
sudo service nginx reload
```

## Настройка CI/CD
1. Файл `workflow` уже написан и находится в директории:
```bash
foodgram-project-react/.github/workflows/foodgram_workflow.yml
```
2. Для адаптации его к вашему серверу добавьте секреты в `GitHub Actions`:
```bash
DOCKER_USERNAME   - имя пользователя в DockerHub
DOCKER_PASSWORD   - пароль пользователя в DockerHub
HOST              - IP-адрес сервера
USER              - имя пользователя
SSH_KEY           - содержимое приватного SSH-ключа
SSH_PASSPHRASE    - пароль для SSH-ключа

TELEGRAM_TO       - ID вашего телеграм-аккаунта (можно узнать у @userinfobot, команда /start)
TELEGRAM_TOKEN    - токен вашего бота (получить токен можно у @BotFather, команда /token, имя бота)
```
3. При первом push'е в `master` будет выполнен полный деплой проекта.

## Примеры тестовых запросов и ответов (в формате `json`)
1. Получение списка всех рецептов по `GET-запросу`:
```r
https://foodgramou.myvnc.com/api/recipes/
```
Ответ:
```json
{
    "id": 7,
    "author": {
        "id": 2,
        "email": "alina@alina.alina",
        "username": "Alina",
        "first_name": "Alina",
        "last_name": "Pronina",
        "is_subscribed": false
    },
    "name": "Азу",
    "image": "/media/recipes/temp_Hkh0BQH.jpeg",
    "text": "Азу по-татарски",
    "ingredients": [
        {
            "id": 1102,
            "name": "мясо",
            "measurement_unit": "г",
            "amount": 500
        }
    ],
    "tags": [
        {
            "id": 3,
            "name": "Ужин",
            "color": "#32CD32",
            "slug": "dinner"
        }
    ],
    "cooking_time": 60,
    "is_favorited": false,
    "is_in_shopping_cart": false
}
```
2. Получение рецепта по `id` `GET-запрос`:
```r
https://foodgramou.myvnc.com/api/recipes/7/
```
Ответ:
```json
{
    "id": 7,
    "author": {
        "id": 2,
        "email": "alina@alina.alina",
        "username": "Alina",
        "first_name": "Alina",
        "last_name": "Pronina",
        "is_subscribed": false
    },
    "name": "Азу",
    "image": "/media/recipes/temp_Hkh0BQH.jpeg",
    "text": "Азу по-татарски",
    "ingredients": [
        {
            "id": 1102,
            "name": "мясо",
            "measurement_unit": "г",
            "amount": 500
        }
    ],
    "tags": [
        {
            "id": 3,
            "name": "Ужин",
            "color": "#32CD32",
            "slug": "dinner"
        }
    ],
    "cooking_time": 60,
    "is_favorited": false,
    "is_in_shopping_cart": false
}
```

## Об авторе
[Olga-Ustinova](https://github.com/Olga-Ustinova)
