# AskPupkin

Решение домашнего задания ОЦ ВК по курсу "Веб-технологии". Ковалев Артём, ВЕБ-12.

## Как запустить

Для запуска проекта на локальной машине выполните следующие шаги.

### Клонирование репозитория

```bash
git clone https://github.com/artiomkovalev/VK_WEB_2025.git
cd vk-web-1
```

### Настройка PostgreSQL

1.  [Установите PostgreSQL](https://www.postgresql.org/download/)
2.  Создайте пользователя и базу данных для проекта. Войдите в консоль `psql`:

    ```sql
    CREATE USER admin WITH PASSWORD 'admin';
    CREATE DATABASE questions_db OWNER admin;
    ```

### Настройка виртуального окружения и установка зависимостей

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Конфигурация проекта

1.  Откройте файл `askpupkin/settings.py`.
2.  Найдите секцию `DATABASES` и впишите данные для подключения к базе данных

    ```python
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'questions_db',
            'USER': 'admin',
            'PASSWORD': 'admin',
            'HOST': 'localhost',
            'PORT': '5432',
        }
    }
    ```

### Подготовка базы данных

1.  **Примените миграции:**
    ```bash
    python manage.py migrate
    ```

2.  **Наполните базу:**
    ```bash
    python manage.py fill_db 1000
    ```

### Запуск сервера

```bash
python manage.py runserver
```

После этого сайт будет доступен по адресу **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**.
