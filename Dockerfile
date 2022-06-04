FROM nginx:1.22-alpine
WORKDIR /usr/share/nginx/html
COPY docs .
