# Проект "Платформа для онлайн-обучения"

## Описание:
Простая система управления обучением с REST API для курсов и уроков, реализованная на Django REST Framework

Курсы: Полный CRUD (Create, Read, Update, Delete) для учебных курсов

Уроки: Полный CRUD для уроков с привязкой к курсам

Связи: Один курс - много уроков (один-ко-многим)

Для модели курса добавлен в сериализатор поле вывода количества уроков
Добавлена новая модель ПЛАТЕЖИ в приложение users
Для сериализатора для модели курса реализовано поле вывода уроков
Настроена фильтрация для эндпоинта вывода списка платежей
В проекте использована JWT-авторизация
Заведена группа модераторов и описаны права
Описаны права доступа для объектов таким образом, чтобы пользователи, которые не входят в группу модераторов,
могли видеть, редактировать и удалять только свои курсы и уроки
Реализована дополнительная проверка на отсутствие в материалах ссылок на сторонние ресурсы, кроме youtube.com.
Добавлена модель подписки на обновления курса для пользователя.
Реализована пагинация для вывода всех уроков и курсов.
Написаны тесты, которые проверяют корректность работы CRUD уроков и функционал работы подписки на обновления курса.
Подключен и настроен вывод документации для проекта  
```
http://127.0.0.1:8000/swagger/
```
или 
```
http://127.0.0.1:8000/redoc/
```
Подключена возможность оплаты курсов через Stripe
Проект настроен для работы с Celery
Добавлена асинхронная рассылка писем пользователям об обновлении материалов курса
Реализована фоновая задача, которая проверяет пользователей по дате последнего входа по полю 
last_login и, если пользователь не заходил более месяца, блокирует его с помощью флага is_active

## Установка:

1. Клонируйте репозиторий:
```
git@github.com:Elena-Kandrushina/online_learning_platform.git
```

2. Установите зависимости:
```
poetry install
```
## Запуск проекта через Docker Compose
## Отредактируйте файл .env и заполните минимальные настройки:
```
SECRET_KEY=ваш-секретный-ключ
DEBUG=True
NAME=learning_platform
USER=postgres
PASSWORD=postgres
HOST=db
PORT=5432
```
## Основная команда для запуска:
```
docker-compose up -d
```
## Проверка статуса запуска:
```
docker-compose ps
```
## Проверка работоспособности каждого сервиса:
Проверка бэкенда (Django):
откройте в браузере: http://localhost:8000
Проверка логов бэкенда:
```
docker-compose logs --tail=10 backend
```
Создание суперпользователя:
```
docker-compose exec backend python manage.py createsuperuser
```
Админка:
http://localhost:8000/admin/
## Проверка базы данных:
```
docker-compose exec db psql -U postgres -d learning_platform -c "SELECT version();"
```
## Проверка Redis:
```
docker-compose exec redis redis-cli ping
```
## Проверка Celery Worker(логи):
```
docker-compose logs --tail=10 celery
```
## Проверка Celery Beat (вывод логов):
```
docker-compose logs --tail=10 celery-beat
```

## Настройка сервера:
Установите Docker и Docker Compose
Настройка systemd сервиса:
Создайте файл /etc/systemd/system/online-learning.service:
```
[Unit]
Description=Online Learning Platform Docker Compose
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/kandr/online_learning_platform
ExecStart=/usr/bin/docker-compose --env-file .env.prod up -d
ExecStop=/usr/bin/docker-compose down
User=kandr
Group=docker
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```
Запуск сервиса:
```
sudo systemctl daemon-reload
sudo systemctl enable online-learning.service
sudo systemctl start online-learning.service
```
## CI/CD с GitHub Actions
Добавьте следующие секреты:
SERVER_HOST, SERVER_USER, SSH_PRIVATE_KEY, SECRET_KEY
При каждом push в любую ветку запускаются тесты, после успешных тестов происходит деплой

# Проверка статуса на сервере
```
sudo systemctl status online-learning.service
```
# Просмотр логов
```
sudo journalctl -u online-learning.service -n 50 --no-pager
```
# Все логи
```
docker-compose logs
```
# Отдельные сервисы
```
docker-compose logs web
docker-compose logs nginx
docker-compose logs db
```

## Документация:

Дополнительную информацию о структуре проекта можно найти в [документации](docs/README.md).

## Лицензия:

Проект распространяется под [лицензией MIT](LICENSE).