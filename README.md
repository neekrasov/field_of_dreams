# Телеграмм-бот для игры в "Поле чудес"

## Технический стек:
`Python/asyncio`, `Aiohttp`, `DI`, `Aio Pika (RabbitMQ)`, `SQLAlchemy (PostgreSQL)`, `Redis`, `Docker / docker-compose`, `Github-Actions`

## Реализовано:
1. Бот с полноценным геймплеем и защитой от спама (троттлингом).
2. Отдельный сервис для пуллинга Telegram-API с RabbitMQ.
3. Сервис API для администратора.
4. Авто-деплой и загрузка образа в registry с помощью Github-Actions.

## Запуск

### Локально через запуск отдельных сервисов.
1. Клонировать репозиторий.
```
~$ git clone https://github.com/neekrasov/field_of_dreams.git
```
2. Создать .env в корне на примере .env.example и экспортировать ENV.
```
~$ mv .env.example .env && export ENV=1
```
3. Запустить сервисы.
```
~$ make -j 3 run-amqp run-bot run-api
```

### В докер-контейнерах.
1. Клонировать репозиторий.
```
~$ git clone https://github.com/neekrasov/field_of_dreams.git
```
2. Создать dev.env в deploy/ на примере deploy/.env.example и экспортировать ENV.
```
~$ mv deploy/.env.example deploy/dev.env && export ENV=1
```
3. Собрать и запустить контейнеры.
```
~$ make compose-up
```

### На сервере с помощью github-actions.
P.S на сервере с помощью actions можно запустить сконфигурировав
секреты (крененшиалы для сервера) в github-secrets, необходимые секреты:

1. SERVER_USER
2. SERVER_IP
3. SERVER_SSH_KEY
4. SERVER_SSH_PORT

Также необходим файл prestart.sh в в домашней директории.

Пример содержимого:
```
cd /home/user/code/field_of_dreams
make compose-down
make compose-pull
make compose-up
```
Активация экшена на пуш и на ручной вызов через GUI в github.
