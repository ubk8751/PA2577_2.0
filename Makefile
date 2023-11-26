.PHONY: help build deploy run stop clean create

# Combined targets
all: build deploy
allrun: build run

# Build targets
build:
	docker build -t flask-app -f ./app/Dockerfile ./app

# Deploy targets
deploy:
	kubectl apply -f ./kubernetes/secrets.yaml
	kubectl apply -f ./kubernetes/persistent-volume.yaml
	kubectl apply -f ./kubernetes/postgresql-deployment.yaml
	kubectl apply -f ./kubernetes/flaskapp-deployment.yaml
# kubectl get svc -w

# Run the application locally
run:
	kubectl port-forward service/flask-app-service 5000:5000 & python app/src/app.py

# Stop the running containers
stop:
	docker-compose down

# Clean up deployed resources
clean:
	kubectl delete -f ./kubernetes/secrets.yaml
	kubectl delete -f ./kubernetes/postgresql-deployment.yaml
	kubectl delete -f ./kubernetes/flaskapp-deployment.yaml
	kubectl delete -f ./kubernetes/persistent-volume.yaml
# pkill -f 'kubectl port-forward'

# Display help message
help:
	@echo "Available targets:"
	@echo "  - build: Build the Docker image for the Flask app."
	@echo "  - deploy: Deploy the application on Kubernetes."
	@echo "  - run: Run the application locally using kubectl port-forward."
	@echo "  - stop: Stop the kubectl port-forward process."
	@echo "  - clean: Clean up deployed resources on Kubernetes."
	@echo "  - create: Build and deploy the application."
