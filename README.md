# Система управления учётными данными

## Описание

Данный проект представляет собой локально развернутую систему управления учётными данными, реализованную с использованием современных технологий контейнеризации и оркестрации: Docker, Kubernetes (k3d), Traefik, PostgreSQL, Prometheus и Grafana.

**Компоненты системы:**

*   **Traefik:** Ingress Controller / Load Balancer.
*   **userapi:** Самописный бэкенд на FastAPI для управления пользователями.
*   **PostgreSQL:** База данных для хранения учётных данных.
*   **Prometheus:** Система сбора метрик.
*   **Grafana:** Система визуализации метрик из Prometheus.

## Требования

*   **Docker Desktop** (с включенным WSL 2 backend)
*   **Windows PowerShell** (или терминал WSL2)
*   **kubectl**
*   **helm**
*   **k3d**
*   **GitHub Actions Runner (локальный)** — для выполнения шага деплоя в локальный кластер k3d.

## Установка и запуск

### 1. Подготовка окружения

1.  **Запустите Docker Desktop** на вашем Windows-хосте и дождитесь полной загрузки (индикатор в трее станет статичным).
2.  **Откройте PowerShell** (или терминал WSL2, если вы там работаете).

### 2. Создание k3d-кластера и установка Traefik

1.  **Создайте кластер k3d:**
    ```bash
    k3d cluster create traefik \
      --port 80:80@loadbalancer \
      --port 443:443@loadbalancer \
      --port 8000:8000@loadbalancer \
      --k3s-arg "--disable=traefik@server:0"
    ```
    *Эта команда создаст кластер с именем `traefik`, откроет порты 80, 443, 8000 на хосте и отключит встроенный Traefik в k3s.*

2.  **Проверьте контекст `kubectl`:**
    ```bash
    kubectl cluster-info --context k3d-traefik
    ```

3.  **Добавьте репозиторий Helm для Traefik и создайте namespace:**
    ```bash
    helm repo add traefik https://traefik.github.io/charts
    helm repo update
    kubectl create namespace traefik
    ```

4. **Установите Traefik с помощью Helm:**
    ```bash
    helm install traefik traefik/traefik \
      --namespace traefik \
      --values values.yaml
    ```

### 3. Запуск `userapi`

1.  **Перейдите в директорию `app`:**
    ```bash
    cd /mnt/c/Users/Inquisitor/Desktop/CourseWork/Project/app
    ```

2.  **Соберите Docker-образ `userapi`:**
    ```bash
    docker build -t userapi:latest .
    ```

3.  **Импортируйте образ в кластер k3d:**
    ```bash
    # Вернитесь в директорию Project
    cd ..
    k3d image import userapi:latest --cluster traefik
    ```

### 4. Запуск PostgreSQL

1.  **Создайте Secret для PostgreSQL:**
    ```bash
    kubectl create secret generic postgres-secret \
      --from-literal=POSTGRES_PASSWORD=your_secure_password \
      --from-literal=POSTGRES_USER=your_db_user \
      --from-literal=POSTGRES_DB=your_db_name \
      -n traefik
    ```
    *Замените `your_secure_password`, `your_db_user`, `your_db_name` на реальные значения.*


### 5. Запуск `userapi`

1.  **Примените:**
    ```bash
    kubectl apply -f userapi-deployment.yaml
    ```

2.  **Примените:**
    ```bash
    kubectl apply -f userapi-service.yaml
    ```

3.  **Примените:**
    ```bash
    kubectl apply -f userapi-httproute.yaml
    ```

### 6. Установка Prometheus и Grafana

1.  **Создайте namespace `monitoring`:**
    ```bash
    kubectl create namespace monitoring
    ```

2.  **Добавьте репозиторий Helm для Prometheus Community:**
    ```bash
    helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
    helm repo update
    ```

3.  **Установите `kube-prometheus-stack`:**
    ```bash
    helm install prometheus-stack prometheus-community/kube-prometheus-stack -n monitoring --create-namespace
    ```

## Использование

### API `userapi`

*   **Получить список пользователей:** `curl http://userapi.docker.localhost/users`
*   **Добавить пользователя:**
    ```bash
    curl -X POST http://userapi.docker.localhost/users \
      -H "Content-Type: application/json" \
      -d '{"username": "testuser", "email": "test@example.com"}'
    ```
*   **Проверить подключение к БД:** `curl http://userapi.docker.localhost/health`

### Панель управления Traefik (только HTTP)

*   Откройте `http://dashboard.docker.localhost` в браузере.
*   Так как `api.insecure=true`, аутентификация отключена.

### Grafana

*   Запустите port-forward:
    ```bash
    kubectl port-forward -n monitoring svc/prometheus-stack-grafana 3000:80
    ```
*   Откройте `http://localhost:3000` в браузере.
*   Логин: `admin`
*   Пароль: `prom-operator` 
* (или получите из Secret: `kubectl get secret --namespace monitoring prometheus-stack-grafana -o jsonpath="{.data.admin-password}" | base64 --decode`)

## CI/CD Pipeline

Ваш проект настроен на автоматический CI/CD процесс при каждом push в ветку `main`. Процесс включает:

1.  **Сборку** Docker-образа `userapi`.
2.  **Тестирование** (на данный момент, тесты не используются, но можно добавить в будущем).
3.  **Пуш** образа в Docker Hub.
4.  **Деплой** обновленного `userapi` в ваш локальный k3d-кластер.

### Как это работает

1.  **GitHub Actions Runner (локальный):** Для выполнения шага деплоя в локальный кластер k3d необходимо установить **локальный GitHub Actions Runner** на вашем Windows-ноутбуке (или WSL2). Это специальный агент, который позволяет GitHub Actions выполнять задачи непосредственно на вашей машине, имея доступ к Docker, k3d и kubectl.
2.  **Настройка Secrets:** В настройках репозитория GitHub (`Settings` -> `Secrets and variables` -> `Actions`) добавьте следующие секреты:
    *   `DOCKER_USERNAME`: ваше имя пользователя Docker Hub.
    *   `DOCKER_PASSWORD`: ваш токен доступа к Docker Hub.
    *   `TEST_DB_USER`: тестовое имя пользователя для PostgreSQL (например, `test_user`).
    *   `TEST_DB_PASSWORD`: тестовый пароль для PostgreSQL (например, `test_password`).
    *   `TEST_DB_NAME`: тестовое имя базы данных (например, `test_db`).

### Инструкция по настройке локального раннера

1.  Перейдите в настройки вашего репозитория на GitHub -> `Settings` -> `Actions` -> `Runners`.
2.  Нажмите `New self-hosted runner`.
3.  Выберите ОС (Linux, если WSL2; Windows, если раннер на хосте). Следуйте инструкциям по скачиванию, настройке и запуску раннера.
4.  Убедитесь, что `kubectl` и `k3d` установлены и работают в среде, где будет работать раннер (WSL2 или Windows).

vze