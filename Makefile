build-ui:
	docker-compose build flask-ui

build-app:
	docker-compose build flask-api

build-db:
	docker-compose build postgresql

build-all:
	docker-compose build

build: build-ui build-app build-db

rebuild:
	docker-compose build --no-cache

up:
	docker-compose up --build

stop:
	docker-compose down
	docker system prune -f