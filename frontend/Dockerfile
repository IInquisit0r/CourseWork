FROM nginx:alpine

# Создаём папку для фронтенда и кладём простую заглушку
RUN mkdir -p /usr/share/nginx/html \
    && echo "<!DOCTYPE html><html><head><title>Frontend</title></head><body><h1>Frontend placeholder</h1></body></html>" > /usr/share/nginx/html/index.html

COPY nginx.conf /etc/nginx/conf.d/default.conf

# Устанавливаем рабочий порт (опционально, nginx уже слушает 80)
EXPOSE 80
