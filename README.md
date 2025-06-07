# Telegram Bot для управления Google Calendar

## Описание проекта

Этот проект представляет собой Telegram бота, разработанного для удобного взаимодействия с Google Calendar. Бот позволяет пользователям выполнять базовые операции с календарем непосредственно из Telegram, включая просмотр событий на ближайшую неделю, создание новых событий и удаление существующих. Проект включает в себя функционал для администраторов, такой как рассылка сообщений всем пользователям и просмотр статистики использования бота. Бот поддерживает многоязычность и использует базу данных для хранения информации о пользователях и статистике.

## Участники проекта

- [Медведева Ксения Андреевна]
- [ФИО Участника 2]
- ...

## Инструкция по запуску

Для запуска проекта выполните следующие шаги:

1.  **Клонируйте репозиторий:**

    ```bash
    git clone [ссылка на ваш репозиторий]
    cd [название папки проекта]
    ```

2.  **Создайте виртуальное окружение (рекомендуется):**

    ```bash
    python -m venv .venv
    source .venv/bin/activate  # Для Linux/macOS
    # .venv\Scripts\activate  # Для Windows
    ```

3.  **Установите зависимости:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Настройте переменные окружения:**

    Создайте файл `.env` в корневой директории проекта и добавьте следующие переменные:

    ```env
    BOT_TOKEN=Ваш_токен_бота_Telegram
    ADMIN_IDS=ID_администратора1,ID_администратора2 # Через запятую, без пробелов
    # Настройки Google Calendar API (если используется)
    GOOGLE_CLIENT_ID=Ваш_Client_ID
    GOOGLE_CLIENT_SECRET=Ваш_Client_Secret
    ```

    *Инструкции по получению токена бота и учетных данных Google Calendar можно найти в официальной документации Telegram Bot API и Google Cloud Platform соответственно.*

5.  **Инициализация базы данных (при первом запуске или изменении моделей):**
    
    ```bash
    python -m database.create_db 
    ```
    

6.  **Запуск бота:**

    ```bash
    python -u bot.py
    ```

## Инструкция по настройке

### 1. Создание Telegram бота

1. Откройте Telegram и найдите @BotFather
2. Отправьте команду `/newbot`
3. Следуйте инструкциям:
   - Введите имя бота (например, "Мой Календарь")
   - Введите username бота (должен заканчиваться на 'bot', например "my_calendar_bot")
4. После создания бот выдаст вам `BOT_TOKEN` - сохраните его, он понадобится для `.env` файла

### 2. Как узнать свой Telegram ID

1. Найдите в Telegram бота @userinfobot
2. Отправьте ему любое сообщение
3. Бот ответит вам вашим ID
4. Этот ID нужно добавить в `.env` файл в параметр `ADMIN_IDS`

### 3. Настройка Google Calendar API

#### Создание проекта
1. Перейдите на [Google Cloud Console](https://console.cloud.google.com/)
2. Создайте новый проект:
   - Нажмите "Select a project" → "New Project"
   - Введите название проекта
   - Нажмите "Create"

#### Настройка OAuth consent screen
1. В меню слева выберите "APIs & Services" → "OAuth consent screen"
2. Выберите "External" тип
3. Заполните обязательные поля:
   - App name
   - User support email
   - Developer contact information
4. Добавьте scope: `https://www.googleapis.com/auth/calendar`
5. Добавьте тестовых пользователей (ваш email)

#### Создание учетных данных
1. В меню слева выберите "APIs & Services" → "Credentials"
2. Нажмите "Create Credentials" → "OAuth client ID"
3. Выберите тип приложения "Web application"
4. Добавьте Authorized redirect URIs:
   - `http://localhost:8080/` (для разработки)
   - URL вашего приложения (для продакшена)

#### Сохранение учетных данных
После создания вы получите:
- Client ID
- Client Secret

Сохраните их в `.env` файл:
```env
GOOGLE_CLIENT_ID=ваш_client_id
GOOGLE_CLIENT_SECRET=ваш_client_secret
```

## Структура репозитория

Проект следует следующей структуре:

```
.
├── config/
│   └── settings.py        # Настройки и загрузка переменных окружения
├── database/
│   ├── __init__.py
│   ├── database.py        # Конфигурация базы данных
│   ├── models.py          # Определение моделей SQLAlchemy
│   └── repositories.py    # Логика взаимодействия с базой данных
├── filters/
│   └── admin_filter.py    # Фильтры сообщений (например, для админов)
├── keyboards/
│   └── reply.py           # Определение клавиатур (ReplyKeyboardMarkup)
├── locales/
│   ├── en.py              # Английская локализация
│   └── ru.py              # Русская локализация
├── middlewares/
│   ├── throttling.py      # Пример middleware (ограничение запросов)
│   └── user_middleware.py # Middleware для работы с пользователями и сессией БД
├── routers/
│   ├── __init__.py
│   └── commands.py        # Основные роутеры для команд и сообщений
├── services/
│   └── calendar_api.py    # Взаимодействие с внешними API (Google Calendar)
├── states/
│   ├── admin_states.py    # Состояния FSM для админских функций
│   ├── calendar_states.py # Состояния FSM для функций календаря
│   └── language_states.py # Состояния FSM для выбора языка
├── utils/
│   └── i18n.py            # Утилиты для интернационализации (i18n)
├── .env.example           # Пример файла с переменными окружения
├── .gitignore             # Файл для игнорирования в Git
├── bot.py                 # Основной файл запуска бота
├── Dockerfile             # (Если есть) Файл для сборки Docker-образа
├── README.md              # Этот файл
└── requirements.txt       # Зависимости проекта
```
