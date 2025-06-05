import json
import os
import asyncio
import logging
import mysql.connector
from datetime import datetime
from html.parser import HTMLParser
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes, ChatMemberHandler, CallbackQueryHandler,
    ConversationHandler, MessageHandler, filters, Application
)
from telegram.error import BadRequest

# --- Настройка логирования ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# --- Конфигурация ---
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "12345sport"
DB_NAME = "my_new_database"
BOT_TOKEN = "7556706480:AAHq2ZKWai4YaFsJMVCihFAUb5sOC8MLdYA"
ADMIN_IDS = [1454893897]
WELCOME_FILE = 'welcome_config.json'
TELEGRAM_MESSAGE_LIMIT = 4096  # Лимит символов в сообщении Telegram
# The above code is a Python script that seems to be setting up a quiz or trivia game. It defines a
# question and expects an answer to be provided. The answer is currently empty and needs to be filled
# in.

# --- Данные для викторины ---
QUIZ_QUESTION = 0
quiz_questions = [
    ("В каком году Decentrathon впервые стал заметным событием на IT-сцене Казахстана, и сколько участников и команд он собрал в тот год??", ["В 2023 году", "В 2022 году", "В 2021 году"], 0),
    ("Где можно зарегистрироваться?", ["@decentra_world_bot", "github.com", "Google"], 0),
    ("Кто может участвовать?", ["Все", "Только студенты", "Только специалисты"], 0),
]
user_scores = {}  # Хранение очков пользователей

# --- Данные для гида ---
GUIDE_STEP = 0
guide_steps = [
    "Добро пожаловать в Decentrathon! Это конкурс для разработчиков.",
    "Первый этап — регистрация на сайте decentrathon.kz.",
    "Второй этап — разработка проекта в течение июля.",
    "Финал проходит в августе с демонстрацией результатов.",
    "Удачи и вдохновения!"
]

# --- Данные для FAQ ---
FAQ = """
❓ *Вопросы и ответы по Decentrathon*

1️⃣ Как зарегистрироваться?  
- Зарегистрироваться можно на официальном сайте decentrathon.kz.

2️⃣ Каковы дедлайны?  
- Регистрация до 15 июня, этап разработки — июль, финал — август.

3️⃣ Кто может участвовать?  
- Любой желающий, с соблюдением правил конкурса.
"""

# --- Данные для /about ---
ABOUT_TEXT = """
Decentrathon — это конкурс для разработчиков, направленный на создание децентрализованных приложений и проектов.

Подробности: https://decentrathon.kz
"""

# --- Данные для /contacts ---
CONTACTS_TEXT = """
📞 Контакты организаторов Decentrathon:

- Email: support@decentrathon.kz  
- Telegram: @DecentrathonSupport  
- ВКонтакте: vk.com/decentrathon  
"""

# --- Данные для напоминаний ---
REMINDERS = [
    {"date": "2025-06-15", "message": "📅 Дедлайн регистрации на Decentrathon: 15 июня!"},
    {"date": "2025-07-01", "message": "📅 Начало этапа разработки: 1 июля!"},
    {"date": "2025-08-01", "message": "📅 Финал Decentrathon: август!"},
]

# --- Данные для /feedback ---
FEEDBACK_MESSAGE = 0

# --- Фильтр повторяющихся сообщений ---
last_user_messages = {}
tracked_texts = ["здравствуйте", "🏆", "⚽", "🏀"]


# --- Инициализация конфигурации ---
if not os.path.exists(WELCOME_FILE):
    default_config = {
        "text": (
            "👋 Добро пожаловать в Decentrathon!\n\n"
            "Это комьюнити про технологии, движение и идеи. "
            "Здесь ты можешь делиться своими проектами, участвовать в ивентах и вдохновляться другими! \n\n"
            "❓ Что такое Decentrathon?\n"
            " Decentrathon — крупнейший многопрофильный хакатон в Казахстане."
            "Это соревнование для IT-энтузиастов.\n\n"
            "Это настоящий технологический марафон, где ты, работая соло или в команде, за 48–72 часа создаёшь решения реальных задач.\n\n"
            "Хакатон проходит одновременно в Астане, Алматы, Шымкенте, Караганде, Актобе, Атырау, Павлодаре, Семее и других городах Казахстана — это крупнейшее IT-событие Центральной Азии!\n\n"
            "• <a href='https://t.me/decentra_world_bot/app'>Платформа для хакатонов</a>\n"
            "• <a href='https://t.me/+udwyw0P7MAIzNzYy'>Чат сообщества</a>\n"
            "🤝 <b>Сотрудничество и реклама:</b> @sammExe\n\n"
            "Последний хакатон: <a href='https://astanahub.com/ru/article/decentrathon-3-0-startuet-natsionalnyi-onlain-khakaton-s-prizovym-fondom-16-millionов-tenge'>Decentrathon 3.0</a>\n\n"
            "Присоединяйся к движению и создавай будущее вместе с нами!"
        ),
        "buttons": [
            {"text": "🚀 Платформа хакатонов", "url": "https://t.me/decentra_world_bot/app"},
            {"text": "📚 Архив ивентов", "url": "https://www.instagram.com/decentrathon/?igsh=M2tmMXUydTVkNjZp"},
            {"text": "💬 Присоединиться к чату", "url": "https://t.me/+udwyw0P7MAIzNzYy"}
        ]
    }
    try:
        with open(WELCOME_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=2, ensure_ascii=False)
        logger.info("Конфигурационный файл создан.")
    except Exception as e:
        logger.error(f"Ошибка при создании конфигурации: {e}")

def load_config():
    """Загружает конфигурацию приветствия."""
    try:
        with open(WELCOME_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Ошибка загрузки конфигурации: {e}")
        return {"text": "Ошибка конфигурации.", "buttons": []}

def save_config(config):
    """Сохраняет конфигурацию приветствия."""
    try:
        with open(WELCOME_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Ошибка сохранения конфигурации: {e}")

# --- Валидация HTML ---
class HTMLValidator(HTMLParser):
    """Проверяет HTML на корректность для Telegram."""
    def __init__(self):
        super().__init__()
        self.stack = []
        self.errors = []
        self.allowed_tags = {'b', 'i', 'a', 'br', 'strong', 'em', 'code', 'pre', 's', 'u', 'tg-spoiler', 'tg-emoji'}
        self.nesting_level = 0
        self.max_nesting = 1  # Запрещаем вложенные теги

    def handle_starttag(self, tag, attrs):
        if tag not in self.allowed_tags:
            self.errors.append(f"Неподдерживаемый тег: <{tag}>")
            return
        if self.nesting_level >= self.max_nesting:
            self.errors.append(f"Запрещено вложение тегов: <{tag}> на уровне {self.nesting_level + 1}")
        self.stack.append(tag)
        self.nesting_level += 1

    def handle_endtag(self, tag):
        if not self.stack:
            self.errors.append(f"Закрывающий тег </{tag}> без открывающего")
            return
        if self.stack[-1] != tag:
            self.errors.append(f"Несоответствие тегов: ожидался </{self.stack[-1]}>, получен </{tag}>")
        self.stack.pop()
        self.nesting_level -= 1

    def validate(self, html_text):
        self.feed(html_text)
        self.close()
        if self.stack:
            self.errors.append(f"Не закрыты теги: {', '.join(self.stack)}")
        return not self.errors, self.errors

def validate_html(html_text):
    """Валидирует HTML и возвращает результат."""
    validator = HTMLValidator()
    is_valid, errors = validator.validate(html_text)
    return is_valid, errors

# --- Утилиты базы данных ---
def get_db_connection():
    """Устанавливает соединение с базой данных."""
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            connection_timeout=5
        )
        logger.info("Подключение к базе данных установлено.")
        return conn
    except mysql.connector.Error as err:
        logger.error(f"Ошибка подключения к БД: {err}")
        return None

async def create_tables():
    """Создает таблицы users и events."""
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id BIGINT PRIMARY KEY,
                    username VARCHAR(255),
                    first_name VARCHAR(255),
                    last_name VARCHAR(255),
                    joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    notify_events BOOLEAN DEFAULT TRUE,
                    subscribed BOOLEAN DEFAULT FALSE
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    event_date DATE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()
            logger.info("Таблицы users и events проверены/созданы.")
        except mysql.connector.Error as err:
            logger.error(f"Ошибка создания таблиц: {err}")
        finally:
            cursor.close()
            conn.close()

async def add_user_to_db(user_id: int, username: str, first_name: str, last_name: str = None):
    """Добавляет пользователя в БД."""
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
            if cursor.fetchone():
                logger.debug(f"Пользователь {user_id} уже в БД.")
                return
            sql = """
                INSERT INTO users (id, username, first_name, last_name)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql, (user_id, username, first_name, last_name))
            conn.commit()
            logger.info(f"Пользователь {user_id} добавлен в БД.")
        except mysql.connector.Error as err:
            logger.error(f"Ошибка добавления пользователя: {err}")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()

async def update_user_subscription(user_id: int, subscribed: bool):
    """Обновляет статус подписки пользователя."""
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE users SET subscribed = %s WHERE id = %s", (subscribed, user_id))
            conn.commit()
            logger.info(f"Статус подписки пользователя {user_id} обновлен: {subscribed}")
        except mysql.connector.Error as err:
            logger.error(f"Ошибка обновления подписки: {err}")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()

async def get_subscribed_users():
    """Получает пользователей с активной подпиской."""
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id FROM users WHERE subscribed = TRUE")
            return [row[0] for row in cursor.fetchall()]
        except mysql.connector.Error as err:
            logger.error(f"Ошибка получения подписчиков: {err}")
        finally:
            cursor.close()
            conn.close()
    return []

async def add_event_to_db(name: str, description: str, event_date: str):
    """Добавляет событие в БД."""
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            sql = """
                INSERT INTO events (name, description, event_date)
                VALUES (%s, %s, %s)
            """
            cursor.execute(sql, (name, description, event_date))
            conn.commit()
            logger.info(f"Событие '{name}' добавлено в БД.")
        except mysql.connector.Error as err:
            logger.error(f"Ошибка добавления события: {err}")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()

async def get_users_for_notifications():
    """Получает пользователей с включенными уведомлениями."""
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id FROM users WHERE notify_events = TRUE")
            return [row[0] for row in cursor.fetchall()]
        except mysql.connector.Error as err:
            logger.error(f"Ошибка получения пользователей: {err}")
        finally:
            cursor.close()
            conn.close()
    return []

# --- Вспомогательные функции ---
def is_admin(user_id: int) -> bool:
    """Проверяет, является ли пользователь админом."""
    return user_id in ADMIN_IDS

def main_menu_keyboard():
    """Возвращает клавиатуру главного меню."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("ℹ️ О Decentrathon", url="https://example.com/about_decentrathon")]
    ])

# --- Обработчики бота ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start."""
    config = load_config()
    try:
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton(btn['text'], url=btn['url'])] for btn in config['buttons']]
        )
        await update.message.reply_text(
            config["text"],
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        logger.info(f"Команда /start выполнена пользователем {update.effective_user.id}")
    except BadRequest as e:
        logger.error(f"Ошибка отправки /start: {e}")
        await update.message.reply_text("Ошибка форматирования сообщений. Свяжитесь с админом.")

async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет приветствие новым участникам только в ЛС."""
    result = update.chat_member
    if result.new_chat_member.status == "member" and (not result.old_chat_member or result.old_chat_member.status in ("left", "kicked")):
        user = result.new_chat_member.user
        config = load_config()
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton(btn['text'], url=btn['url'])] for btn in config["buttons"]]
        )
        try:
            await context.bot.send_message(
                chat_id=user.id,
                text=config["text"],
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            logger.info(f"Приветствие отправлено в ЛС пользователю {user.full_name} ({user.id})")
            username = user.username if user.username else None
            first_name = user.first_name if user.first_name else None
            last_name = user.last_name if user.last_name else None
            await add_user_to_db(user.id, username, first_name, last_name)
        except Exception as e:
            logger.warning(f"Не удалось отправить приветствие в ЛС пользователю {user.id}: {e}")

async def set_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда админа для обновления приветствия с валидацией HTML."""
    user = update.effective_user
    if not user or not user.id or not is_admin(user.id):
        await update.message.reply_text("У вас нет прав для выполнения этой команды.")
        return
    if not context.args:
        await update.message.reply_text(
            "Использование: /set_welcome <текст приветствия>\n\n"
            "Поддерживаемые HTML-теги: <b>, <i>, <a href='...'>, <br>.\n"
            "Пример: /set_welcome 👋 Добро пожаловать! <a href='https://example.com'>Ссылка</a>\n"
            "Текст будет проверяться на корректность HTML.",
            parse_mode='Markdown'
        )
        return
    text = " ".join(context.args)
    is_valid, errors = validate_html(text)
    if not is_valid:
        await update.message.reply_text(
            f"⚠️ Ошибки в HTML:\n" + "\n".join([f"• {e}" for e in errors]),
            parse_mode='Markdown'
        )
        return
    config = load_config()
    config["text"] = text
    save_config(config)
    await update.message.reply_text("✅ Приветствие обновлено!")
    logger.info(f"Приветствие обновлено админом {user.id}")

async def set_links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда админа для обновления кнопок."""
    user = update.effective_user
    if not user or not user.id or not is_admin(user.id):
        await update.message.reply_text("У вас нет прав для выполнения этой команды.")
        return
    if not context.args:
        await update.message.reply_text(
            "Использование: /set_links <json кнопок>\n"
            "Пример: `[{\"text\": \"Кнопка\", \"url\": \"https://example.com\"}]`\n"
            "⚠️ Не более 4 кнопок.",
            parse_mode='Markdown'
        )
        return
    try:
        buttons = json.loads(" ".join(context.args))
        for btn in buttons:
            if not isinstance(btn, dict) or 'text' not in btn or 'url' not in btn:
                raise ValueError("Каждый элемент должен содержать 'text' и 'url'.")
            if not isinstance(btn['text'], str) or not isinstance(btn['url'], str):
                raise ValueError("'text' и 'url' должны быть строками.")
        if len(buttons) > 4:
            await update.message.reply_text("⚠️ Рекомендуется до 4 кнопок.", parse_mode='Markdown')
        config = load_config()
        config["buttons"] = buttons
        save_config(config)
        await update.message.reply_text("✅ Кнопки обновлены!")
        logger.info(f"Кнопки обновлены админом {user.id}")
    except json.JSONDecodeError as e:
        await update.message.reply_text(f"⚠️ Ошибка JSON: `{e}`.", parse_mode='Markdown')
    except ValueError as e:
        await update.message.reply_text(f"⚠️ Ошибка валидации: `{e}`", parse_mode='Markdown')

async def preview(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда админа для предпросмотра приветствия."""
    user = update.effective_user
    if not user or not user.id or not is_admin(user.id):
        await update.message.reply_text("У вас нет прав для выполнения этой команды.")
        return
    config = load_config()
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton(btn['text'], url=btn['url'])] for btn in config["buttons"]]
    )
    try:
        await update.message.reply_text(
            config["text"],
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        logger.info(f"Предпросмотр выполнен админом {user.id}")
    except BadRequest as e:
        logger.error(f"Ошибка предпросмотра: {e}")
        await update.message.reply_text("Ошибка форматирования сообщения. Проверьте HTML.")

async def empty_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда админа для очистки списка команд бота."""
    user = update.effective_user
    if not user or not user.id or not is_admin(user.id):
        await update.message.reply_text("У вас нет прав для выполнения этой команды.")
        return
    try:
        await context.bot.set_my_commands(commands=[])
        await update.message.reply_text("✅ Список команд очищен.")
        logger.info(f"Список команд очищен админом {user.id}")
    except BadRequest as e:
        logger.error(f"Ошибка очистки команд: {e}")
        await update.message.reply_text("⚠️ Ошибка при очистке команд. Попробуйте позже.")
    except Exception as e:
        logger.error(f"Неизвестная ошибка в /empty: {e}")
        await update.message.reply_text("⚠️ Неизвестная ошибка. Свяжитесь с поддержкой.")

async def notify_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда админа для добавления события и уведомления пользователей."""
    user = update.effective_user
    if not user or not user.id or not is_admin(user.id):
        await update.message.reply_text("У вас нет прав для выполнения этой команды.")
        return
    if len(context.args) < 3:
        await update.message.reply_text(
            "Использование: /notify <название> <дата YYYY-MM-DD> <описание>\n"
            "Пример: /notify AI Hackathon 2025-12-01 Хакатон по ИИ с призами!",
            parse_mode='Markdown'
        )
        return
    name = context.args[0]
    try:
        event_date = datetime.strptime(context.args[1], '%Y-%m-%d').date()
        description = " ".join(context.args[2:])
        await add_event_to_db(name, description, event_date)
        user_ids = await get_users_for_notifications()
        for user_id in user_ids:
            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=f"📢 Новое событие: <b>{name}</b>\nДата: {event_date}\n{description}",
                    parse_mode='HTML'
                )
                logger.info(f"Уведомление отправлено пользователю {user_id}")
            except Exception as e:
                logger.warning(f"Не удалось отправить уведомление пользователю {user_id}: {e}")
        await update.message.reply_text("✅ Событие добавлено, пользователи уведомлены.")
        logger.info(f"Событие '{name}' добавлено админом {user.id}")
    except ValueError:
        await update.message.reply_text("⚠️ Неверный формат даты. Используйте YYYY-MM-DD.", parse_mode='Markdown')

async def start_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Запускает викторину."""
    user_id = update.effective_user.id
    user_scores[user_id] = 0
    context.user_data['quiz_q'] = 0
    await send_quiz_question(update, context)
    return QUIZ_QUESTION

async def send_quiz_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет вопрос викторины."""
    q_index = context.user_data['quiz_q']
    question, options, _ = quiz_questions[q_index]
    keyboard = [
        [InlineKeyboardButton(opt, callback_data=str(i))] for i, opt in enumerate(options)
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            text=f"Вопрос {q_index+1}:\n{question}", reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            text=f"Вопрос {q_index+1}: {question}", reply_markup=reply_markup
        )

async def quiz_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает ответ на вопрос викторины."""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    selected = int(query.data)
    q_index = context.user_data['quiz_q']
    _, _, correct_index = quiz_questions[q_index]
    if selected == correct_index:
        user_scores[user_id] += 1
    context.user_data['quiz_q'] += 1
    if context.user_data['quiz_q'] < len(quiz_questions):
        await send_quiz_question(update, context)
        return QUIZ_QUESTION
    else:
        score = user_scores.get(user_id, 0)
        await query.edit_message_text(text=f"Викторина окончена! Ваш результат: {score} из {len(quiz_questions)}")
        return ConversationHandler.END

async def start_guide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Запускает интерактивный гид."""
    context.user_data['guide_step'] = 0
    text = guide_steps[0]
    keyboard = [[InlineKeyboardButton("Далее", callback_data="next")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text=text, reply_markup=reply_markup)
    return GUIDE_STEP

async def guide_next(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Переходит к следующему шагу гида."""
    query = update.callback_query
    await query.answer()
    step = context.user_data.get('guide_step', 0) + 1
    if step < len(guide_steps):
        context.user_data['guide_step'] = step
        keyboard = [[InlineKeyboardButton("Далее", callback_data="next")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=guide_steps[step], reply_markup=reply_markup)
        return GUIDE_STEP
    else:
        await query.edit_message_text(text="Спасибо за внимание! Если захотите повторить, используйте /guide.")
        return ConversationHandler.END

async def faq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет FAQ."""
    try:
        text_parts = [FAQ[i:i+TELEGRAM_MESSAGE_LIMIT] for i in range(0, len(FAQ), TELEGRAM_MESSAGE_LIMIT)]
        for part in text_parts:
            await update.message.reply_text(part, parse_mode='Markdown')
        logger.info(f"Команда /faq выполнена пользователем {update.effective_user.id}")
    except Exception as e:
        logger.error(f"Ошибка отправки FAQ: {e}")
        await update.message.reply_text("Ошибка загрузки FAQ. Попробуйте позже.")

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет информацию о Decentrathon."""
    try:
        await update.message.reply_text(ABOUT_TEXT)
        logger.info(f"Команда /about выполнена пользователем {update.effective_user.id}")
    except Exception as e:
        logger.error(f"Ошибка отправки /about: {e}")
        await update.message.reply_text("Ошибка загрузки информации. Попробуйте позже.")

async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Подписывает пользователя на напоминания."""
    user_id = update.effective_user.id
    try:
        await update_user_subscription(user_id, True)
        await update.message.reply_text("Вы подписаны на напоминания!")
        logger.info(f"Пользователь {user_id} подписался на напоминания")
    except Exception as e:
        logger.error(f"Ошибка подписки: {e}")
        await update.message.reply_text("Ошибка при подписке. Попробуйте позже.")

async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отписывает пользователя от напоминаний."""
    user_id = update.effective_user.id
    try:
        await update_user_subscription(user_id, False)
        await update.message.reply_text("Вы отписаны от напоминаний.")
        logger.info(f"Пользователь {user_id} отписался от напоминаний")
    except Exception as e:
        logger.error(f"Ошибка отписки: {e}")
        await update.message.reply_text("Ошибка при отписке. Попробуйте позже.")

async def contacts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет контактную информацию."""
    try:
        await update.message.reply_text(CONTACTS_TEXT)
        logger.info(f"Команда /contacts выполнена пользователем {update.effective_user.id}")
    except Exception as e:
        logger.error(f"Ошибка отправки контактов: {e}")
        await update.message.reply_text("Ошибка загрузки контактов. Попробуйте позже.")

async def start_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Запускает отправку обратной связи."""
    await update.message.reply_text("Пожалуйста, напишите ваше сообщение для организаторов.")
    return FEEDBACK_MESSAGE

async def receive_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получает и пересылает сообщение обратной связи админу."""
    user_id = update.effective_user.id
    username = update.effective_user.username or "Нет имени пользователя"
    text = update.message.text
    try:
        for admin_id in ADMIN_IDS:
            await context.bot.send_message(
                chat_id=admin_id,
                text=f"📩 Обратная связь от @{username} (ID: {user_id}):\n{text}"
            )
        await update.message.reply_text("Спасибо за ваш отзыв! Он отправлен организаторам.")
        logger.info(f"Обратная связь от пользователя {user_id} отправлена админам")
    except Exception as e:
        logger.error(f"Ошибка отправки обратной связи: {e}")
        await update.message.reply_text("Ошибка при отправке отзыва. Попробуйте снова.")
    return ConversationHandler.END

async def delete_repeated(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Удаляет повторяющиеся сообщения."""
    user_id = update.effective_user.id
    text = update.message.text
    try:
        if text and any(t in text.lower() for t in tracked_texts):
            last_text = last_user_messages.get(user_id)
            if last_text == text:
                try:
                    await update.message.delete()
                    logger.info(f"Удалено повторяющееся сообщение от пользователя {user_id}")
                except Exception as e:
                    logger.error(f"Ошибка при удалении сообщения: {user_id}: {e}")
            else:
                last_user_messages[user_id] = text
    except Exception as e:
        logger.error(f"Ошибка в обработке повторяющихся сообщений для пользователя {user_id}: {e}")

async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик callback-запросов."""
    query = update.callback_query
    user_id = query.from_user.id
    try:
        await query.answer()
        await query.message.edit_text(
            text="Команда не доступна.",
            reply_markup=main_menu_keyboard(),
            parse_mode='HTML'
        )
        logger.info(f"Callback запрос от пользователя {user_id} обработан")
    except BadRequest as e:
        logger.error(f"Ошибка в callback-запросе: {e}")
        await query.message.edit_text(
            text="Ошибка обработки запроса.",
            reply_markup=main_menu_keyboard(),
            parse_mode='HTML'
        )
    except Exception as e:
        logger.error(f"Ошибка в callback-запросе для пользователя {user_id}: {e}")
        await query.message.edit_text(
            text="Ошибка обработки запроса.",
            reply_markup=main_menu_keyboard(),
            parse_mode='HTML'
        )

async def main():
    """Основная функция запуска бота."""
    try:
        await create_tables()
        # Инициализация Application
        app = Application.builder().token(BOT_TOKEN).build()

        # Установка команд для меню
        commands = [
            BotCommand("start", "Start the bot and receive a welcome message"),
            BotCommand("quiz", "Start a quiz"),
            BotCommand("guide", "Start an interactive guide"),
            BotCommand("faq", "View frequently asked questions"),
            BotCommand("about", "Learn about Decentrathon"),
            BotCommand("subscribe", "Subscribe to event reminders"),
            BotCommand("unsubscribe", "Unsubscribe from event reminders"),
            BotCommand("contacts", "Get organizers' contact information"),
            BotCommand("feedback", "Send feedback to organizers"),
            BotCommand("set_welcome", "Set a custom welcome message for new members"),
            BotCommand("set_links", "Set quick access links for group messages"),
            BotCommand("preview", "Preview the current welcome message or links"),
            BotCommand("notify", "Create an event and notify users"),
            BotCommand("empty", "Clear all commands")
        ]
        await app.bot.set_my_commands(commands)
        logger.info("Команды бота установлены в меню.")

        # Обработчики команд
        app.add_handler(CommandHandler("start", start))
        app.add_handler(ChatMemberHandler(welcome_new_member, ChatMemberHandler.CHAT_MEMBER))
        app.add_handler(CommandHandler("set_welcome", set_welcome))
        app.add_handler(CommandHandler("set_links", set_links))
        app.add_handler(CommandHandler("preview", preview))
        app.add_handler(CommandHandler("notify", notify_command))
        app.add_handler(CommandHandler("empty", empty_command))
        app.add_handler(CommandHandler("faq", faq))
        app.add_handler(CommandHandler("about", about))
        app.add_handler(CommandHandler("subscribe", subscribe))
        app.add_handler(CommandHandler("unsubscribe", unsubscribe))
        app.add_handler(CommandHandler("contacts", contacts))

        # Обработчик викторины
        quiz_handler = ConversationHandler(
            entry_points=[CommandHandler('quiz', start_quiz)],
            states={
                QUIZ_QUESTION: [CallbackQueryHandler(quiz_answer)],
            },
            fallbacks=[]
        )
        app.add_handler(quiz_handler)

        # Обработчик гида
        guide_handler = ConversationHandler(
            entry_points=[CommandHandler('guide', start_guide)],
            states={
                GUIDE_STEP: [CallbackQueryHandler(guide_next, pattern='^next$')],
            },
            fallbacks=[]
        )
        app.add_handler(guide_handler)

        # Обработчик обратной связи
        feedback_handler = ConversationHandler(
            entry_points=[CommandHandler('feedback', start_feedback)],
            states={
                FEEDBACK_MESSAGE: [MessageHandler(filters.TEXT & (~filters.COMMAND), receive_feedback)],
            },
            fallbacks=[]
        )
        app.add_handler(feedback_handler)

        # Обработчик повторяющихся сообщений
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), delete_repeated))

        # Обработчик callback-запросов
        app.add_handler(CallbackQueryHandler(handle_callback_query))

        logger.info("🤖 Бот запущен и готов к работе!")
        await app.run_polling(drop_pending_updates=True)

    except Exception as e:
        logger.critical(f"Ошибка запуска бота: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    import sys
    import asyncio
    import nest_asyncio

    if sys.platform.startswith("win") and sys.version_info >= (3, 8):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    nest_asyncio.apply()
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except (KeyboardInterrupt, SystemExit):
        print("Бот остановлен")