## Инструкция по запуску приложения в Docker

### UPD: пункты вплоть до добавления таблиц в БД можно заменить командой:

``````
docker-compose up
``````

### Установка образов:

``````
docker pull postgres
docker build --tag flask-image .
``````

### Создание сети:

``````
docker network create --driver=bridge app-network
``````

### Запуск и конфигурация контейнера postgres:

``````
# запуск контейнера
docker run -it --name database_container -p 5432:5432 --network app-network -e POSTGRES_PASSWORD=password postgres

# создание пользователя и базы данных
docker exec -it database sh
psql -U postgres
create database advertisements_db;
create user db_user with createdb;
alter user db_user with password 'db_user_password';
alter database advertisements_db owner to db_user;
``````

### Запуск и настройка контейнера flask:

``````
# запуск контейнера
docker run --name flask -p 5000:5000 --network app-network 
-e DATABASE=postgreql://db_user:db_user_password@database_container/advertisements_db flask-image

# создание таблиц в базе данных
docker exec -it flask sh
flask shell
from app import db
from models import User, Advertisement
db.create_all()
``````