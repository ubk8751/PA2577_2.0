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

deploy:
	kubectl apply -f ./kubernetes/postgres-deployment.yaml
	kubectl apply -f ./kubernetes/postgres-pvc-pv.yaml
	kubectl apply -f ./kubernetes/flask-ui-deployment.yaml
	kubectl apply -f ./kubernetes/flask-user-management-deployment.yaml
	kubectl apply -f ./kubernetes/flask-api-deployment.yaml
	kubectl apply -f ./kubernetes/configmaps.yaml

stop:
	docker-compose down
	docker system prune -f