.PHONY: help build run clean

build:
	docker build -t flask-app:latest ./app

deploy:
	kubectl apply -f kubernetes/secrets.yaml
	kubectl apply -f kubernetes/persistent-volume.yaml
	kubectl apply -f kubernetes/postgresql-deployment.yaml
	kubectl apply -f kubernetes/flaskapp-deployment.yaml
	kubectl get svc -w

create: build deploy

run:
	docker-compose up --build

stop:
	docker-compose down

clean:
	kubectl delete -f kubernetes/secrets.yaml
	kubectl delete -f kubernetes/persistent-volume.yaml
	kubectl delete -f kubernetes/postgresql-deployment.yaml
	kubectl delete -f kubernetes/flaskapp-deployment.yaml
