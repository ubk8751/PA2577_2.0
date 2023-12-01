echo "Building docker container..."
docker-compose build --no-cache

echo "Tagging docker containers..."
docker tag ubk8751/flask-api ubk8751/flask-api:latest
docker tag ubk8751/flask-user-management ubk8751/flask-user-management:latest
docker tag ubk8751/flask-ui ubk8751/flask-ui:latest

echo "Pushing to docker hub..."
docker push ubk8751/flask-api:latest
docker push ubk8751/flask-user-management:latest
docker push ubk8751/flask-ui:latest