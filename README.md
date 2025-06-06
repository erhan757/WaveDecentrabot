# Decentrathon Telegram Bot

Бот для поддержки участников ивентов Decentrathon — крупнейшего многопрофильного хакатона в Казахстане.  
Бот помогает новым участникам, отправляет напоминания, собирает обратную связь и делает общение в чате удобнее.

## Возможности

- Приветственное сообщение для новых пользователей с быстрыми кнопками и ссылками
- Викторина и интерактивные гиды для знакомства с проектом
- Рассылка напоминаний о событиях и дедлайнах
- Ответы на часто задаваемые вопросы (FAQ)
- Поддержка подписки/отписки на новости
- Обратная связь и связь с организаторами
- Фильтрация спама и повторяющихся сообщений

## Быстрый старт

1. **Клонируйте репозиторий:**
   ```bash
   git clone https://github.com/ВАШ_ЛОГИН/ВАШ_РЕПОЗИТОРИЙ.git
   cd ВАШ_РЕПОЗИТОРИЙ
   ```

2. **Установите зависимости:**
   ```bash
   pip install -r requirements.txt
   python-telegram-bot==20.7
   mysql-connector-python
Пояснения:

python-telegram-bot — основной пакет для работы с Telegram API.
mysql-connector-python — для работы с MySQL через Python.
aiohttp, asyncio и стандартные модули (os, json, logging, datetime, html.parser) устанавливать не нужно — они входят в стандартную библиотеку Python.
   ```

3. **Добавьте токен вашего или моего Telegram-бота:**
   - Создайте файл `.env` или внесите токен в переменную окружения `TELEGRAM_BOT_TOKEN`.
4 Добавьте вашу база данных, я брал свой mysql:
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "12345sport"
DB_NAME = "my_new_database"

5. **Запустите бота:**
   ```bash
   python main.py
   ```

## Конфигурация

- Все настройки (например, ссылки для приветствия) находятся в файле `welcome_config.json`.
- Для рассылки напоминаний и хранения данных используется база данных MySQL (проверьте файл `config.py`).

## Структура проекта

- `main.py` — основной файл запуска бота
- `handlers.py` — обработчики команд и сообщений
- `welcome_config.json` — конфиг приветственных сообщений
- `requirements.txt` — список зависимостей

## Дополнительная информация

- [Decentrathon на Instagram](https://www.instagram.com/decentrathon/)
- [Decentrathon на Telegram](https://t.me/decentrathon)

---

**Для вопросов и предложений:**  
Пишите в Issues или напрямую организаторам через команду `/contacts` в боте.
