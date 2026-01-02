from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from database import UserLanguage


def get_language_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="🇺🇸 English", callback_data="lang_en"))
    keyboard.add(InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"))
    keyboard.add(InlineKeyboardButton(text="🇺🇦 Українська", callback_data="lang_uk"))
    return keyboard.adjust(2).as_markup()


def get_main_menu_keyboard(language: str = "en"):
    texts = {
        "en": {
            "products": "📦 Products",
            "categories": "📂 Categories",
            "analytics": "📊 Analytics",
            "settings": "⚙️ Settings"
        },
        "ru": {
            "products": "📦 Товары",
            "categories": "📂 Категории",
            "analytics": "📊 Аналитика",
            "settings": "⚙️ Настройки"
        },
        "uk": {
            "products": "📦 Товари",
            "categories": "📂 Категорії",
            "analytics": "📊 Аналітика",
            "settings": "⚙️ Налаштування"
        }
    }
    
    text = texts.get(language, texts["en"])
    
    keyboard = ReplyKeyboardBuilder()
    keyboard.add(KeyboardButton(text=text["products"]))
    keyboard.add(KeyboardButton(text=text["categories"]))
    keyboard.add(KeyboardButton(text=text["analytics"]))
    keyboard.add(KeyboardButton(text=text["settings"]))
    return keyboard.adjust(2).as_markup()


def get_products_menu_keyboard(language: str = "en"):
    texts = {
        "en": {
            "add": "➕ Add Product",
            "list": "📋 List Products",
            "edit": "✏️ Edit Product",
            "delete": "🗑️ Delete Product",
            "back": "⬅️ Back"
        },
        "ru": {
            "add": "➕ Добавить товар",
            "list": "📋 Список товаров",
            "edit": "✏️ Редактировать",
            "delete": "🗑️ Удалить",
            "back": "⬅️ Назад"
        },
        "uk": {
            "add": "➕ Додати товар",
            "list": "📋 Список товарів",
            "edit": "✏️ Редагувати",
            "delete": "🗑️ Видалити",
            "back": "⬅️ Назад"
        }
    }
    
    text = texts.get(language, texts["en"])
    
    keyboard = ReplyKeyboardBuilder()
    keyboard.add(KeyboardButton(text=text["add"]))
    keyboard.add(KeyboardButton(text=text["list"]))
    keyboard.add(KeyboardButton(text=text["edit"]))
    keyboard.add(KeyboardButton(text=text["delete"]))
    keyboard.add(KeyboardButton(text=text["back"]))
    return keyboard.adjust(2).as_markup()


def get_categories_menu_keyboard(language: str = "en"):
    texts = {
        "en": {
            "add": "➕ Add Category",
            "list": "📋 List Categories",
            "edit": "✏️ Edit Category",
            "back": "⬅️ Back"
        },
        "ru": {
            "add": "➕ Добавить категорию",
            "list": "📋 Список категорий",
            "edit": "✏️ Редактировать",
            "back": "⬅️ Назад"
        },
        "uk": {
            "add": "➕ Додати категорію",
            "list": "📋 Список категорій",
            "edit": "✏️ Редагувати",
            "back": "⬅️ Назад"
        }
    }
    
    text = texts.get(language, texts["en"])
    
    keyboard = ReplyKeyboardBuilder()
    keyboard.add(KeyboardButton(text=text["add"]))
    keyboard.add(KeyboardButton(text=text["list"]))
    keyboard.add(KeyboardButton(text=text["edit"]))
    keyboard.add(KeyboardButton(text=text["back"]))
    return keyboard.adjust(2).as_markup()


def get_analytics_period_keyboard(language: str = "en"):
    texts = {
        "en": {
            "today": "📅 Today",
            "week": "📅 This Week",
          "month": "📅 This Month",
            "year": "📅 This Year",
            "all": "📅 All Time",
            "custom": "📅 Custom Period",
            "back": "⬅️ Back"
        },
        "ru": {
            "today": "📅 Сегодня",
            "week": "📅 Неделя",
            "month": "📅 Месяц",
            "year": "📅 Год",
            "all": "📅 Все время",
            "custom": "📅 Выбрать период",
            "back": "⬅️ Назад"
        },
        "uk": {
            "today": "📅 Сьогодні",
            "week": "📅 Тиждень",
            "month": "📅 Місяць",
            "year": "📅 Рік",
            "all": "📅 Весь час",
            "custom": "📅 Обрати період",
            "back": "⬅️ Назад"
        }
    }
    
    text = texts.get(language, texts["en"])
    
    keyboard = ReplyKeyboardBuilder()
    keyboard.add(KeyboardButton(text=text["today"]))
    keyboard.add(KeyboardButton(text=text["week"]))
    keyboard.add(KeyboardButton(text=text["month"]))
    keyboard.add(KeyboardButton(text=text["year"]))
    keyboard.add(KeyboardButton(text=text["all"]))
    keyboard.add(KeyboardButton(text=text["custom"]))
    keyboard.add(KeyboardButton(text=text["back"]))
    return keyboard.adjust(2).as_markup()


def get_edit_product_fields_keyboard(language: str = "en"):
    texts = {
        "en": {
            "name": "📝 Name",
            "category": "📂 Category",
            "purchase_price": "💰 Purchase Price",
            "sale_price": "🏷️ Sale Price",
            "quantity": "📊 Quantity",
            "sku": "🏷️ SKU",
            "description": "📄 Description",
            "cancel": "❌ Cancel"
        },
        "ru": {
            "name": "📝 Название",
            "category": "📂 Категория",
            "purchase_price": "💰 Цена закупки",
            "sale_price": "🏷️ Цена продажи",
            "quantity": "📊 Количество",
            "sku": "🏷️ Артикул",
            "description": "📄 Описание",
            "cancel": "❌ Отмена"
        },
        "uk": {
            "name": "📝 Назва",
            "category": "📂 Категорія",
            "purchase_price": "💰 Ціна закупівлі",
            "sale_price": "🏷️ Ціна продажу",
            "quantity": "📊 Кількість",
            "sku": "🏷️ Артикул",
            "description": "📄 Опис",
            "cancel": "❌ Скасувати"
        }
    }
    
    text = texts.get(language, texts["en"])
    
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text=text["name"], callback_data="edit_name"))
    keyboard.add(InlineKeyboardButton(text=text["category"], callback_data="edit_category"))
    keyboard.add(InlineKeyboardButton(text=text["purchase_price"], callback_data="edit_purchase_price"))
    keyboard.add(InlineKeyboardButton(text=text["sale_price"], callback_data="edit_sale_price"))
    keyboard.add(InlineKeyboardButton(text=text["quantity"], callback_data="edit_quantity"))
    keyboard.add(InlineKeyboardButton(text=text["sku"], callback_data="edit_sku"))
    keyboard.add(InlineKeyboardButton(text=text["description"], callback_data="edit_description"))
    keyboard.add(InlineKeyboardButton(text=text["cancel"], callback_data="cancel_edit"))
    return keyboard.adjust(2).as_markup()
def get_categories_keyboard(categories, language: str = "en"):
    keyboard = InlineKeyboardBuilder()
    for category in categories:
        keyboard.add(InlineKeyboardButton(
            text=category.name,
            callback_data=f"category_{category.id}"
        ))
    
    texts = {
        "en": {"none": "❌ None", "cancel": "❌ Cancel"},
        "ru": {"none": "❌ Без категории", "cancel": "❌ Отмена"},
        "uk": {"none": "❌ Без категорії", "cancel": "❌ Скасувати"}
    }
    
    text = texts.get(language, texts["en"])
    keyboard.add(InlineKeyboardButton(text=text["none"], callback_data="category_none"))
    keyboard.add(InlineKeyboardButton(text=text["cancel"], callback_data="category_cancel"))
    
    return keyboard.adjust(1).as_markup()
  def get_products_keyboard(products, language: str = "en"):
    keyboard = InlineKeyboardBuilder()
    for product in products:
        keyboard.add(InlineKeyboardButton(
            text=product.name,
            callback_data=f"product_{product.id}"
        ))
    
    texts = {
        "en": {"cancel": "❌ Cancel"},
        "ru": {"cancel": "❌ Отмена"},
        "uk": {"cancel": "❌ Скасувати"}
    }
    
    text = texts.get(language, texts["en"])
    keyboard.add(InlineKeyboardButton(text=text["cancel"], callback_data="product_cancel"))
    
    return keyboard.adjust(1).as_markup()
