FROM nginx:alpine

WORKDIR /app/ui

COPY static/ /usr/share/nginx/html/static
COPY templates/ /usr/share/nginx/html/templates

EXPOSE 80

ENV NAME ui