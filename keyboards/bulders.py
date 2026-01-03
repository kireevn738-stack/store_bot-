from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup
from typing import List, Optional
import config

def get_language_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    for lang_code, lang_name in config.LANGUAGES.items():
        builder.add(KeyboardButton(text=lang_name))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

def get_main_menu_keyboard(language: str = 'ru') -> ReplyKeyboardMarkup:
    texts = {
        'ru': {
            'store': '🏪 Мой магазин',
            'products': '📦 Товары',
            'categories': '📁 Категории',
            'orders': '💰 Заказы',
            'analytics': '📊 Аналитика',
            'settings': '⚙️ Настройки'
        },
        'en': {
            'store': '🏪 My Store',
            'products': '📦 Products',
            'categories': '📁 Categories',
            'orders': '💰 Orders',
            'analytics': '📊 Analytics',
            'settings': '⚙️ Settings'
        }
    }
    
    builder = ReplyKeyboardBuilder()
    text_dict = texts.get(language, texts['ru'])
    
    builder.add(KeyboardButton(text=text_dict['store']))
    builder.add(KeyboardButton(text=text_dict['products']))
    builder.add(KeyboardButton(text=text_dict['categories']))
    builder.add(KeyboardButton(text=text_dict['orders']))
    builder.add(KeyboardButton(text=text_dict['analytics']))
    builder.add(KeyboardButton(text=text_dict['settings']))
    builder.adjust(2, 2, 2)
    
    return builder.as_markup(resize_keyboard=True)

def get_cancel_keyboard(language: str = 'ru') -> ReplyKeyboardMarkup:
    text = "❌ Отмена" if language == 'ru' else "❌ Cancel"
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text=text))
    return builder.as_markup(resize_keyboard=True)

def get_analytics_period_keyboard(language: str = 'ru') -> InlineKeyboardMarkup:
    texts = {
        'ru': {
            'day': '📅 День',
            'week': '📆 Неделя',
            'month': '📊 Месяц',
            'year': '📈 Год',
            'all': '⏳ Все время',
            'custom': '📅 Выбрать период'
        },
        'en': {
            'day': '📅 Day',
            'week': '📆 Week',
            'month': '📊 Month',
            'year': '📈 Year',
            'all': '⏳ All time',
            'custom': '📅 Custom period'
        }
    }
    
    builder = InlineKeyboardBuilder()
    text_dict = texts.get(language, texts['ru'])
    
    for period, text in text_dict.items():
        builder.button(text=text, callback_data=f"analytics_{period}")
    
    builder.adjust(2, 2, 2)
    return builder.as_markup()

def get_product_actions_keyboard(product_id: int, language: str = 'ru') -> InlineKeyboardMarkup:
    texts = {
        'ru': {
            'edit': '✏️ Редактировать',
            'delete': '🗑️ Удалить',
            'sell': '💰 Продать'
        },
        'en': {
            'edit': '✏️ Edit',
            'delete': '🗑️ Delete',
            'sell': '💰 Sell'
        }
    }
    
    builder = InlineKeyboardBuilder()
    text_dict = texts.get(language, texts['ru'])
    
    builder.button(text=text_dict['edit'], callback_data=f"edit_product_{product_id}")
    builder.button(text=text_dict['delete'], callback_data=f"delete_product_{product_id}")
    builder.button(text=text_dict['sell'], callback_data=f"sell_product_{product_id}")
    builder.adjust(2, 1)
    
    return builder.as_markup()

def get_categories_keyboard(categories: List, language: str = 'ru') -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    for category in categories:
        builder.button(text=category.name, callback_data=f"category_{category.id}")
    
    builder.button(
        text="➕ Добавить категорию" if language == 'ru' else "➕ Add category",
        callback_data="add_category"
    )
    
    builder.adjust(1)
    return builder.as_markup()

def get_yes_no_keyboard(language: str = 'ru') -> InlineKeyboardMarkup:
    texts = {
        'ru': {'yes': '✅ Да', 'no': '❌ Нет'},
        'en': {'yes': '✅ Yes', 'no': '❌ No'}
    }
    
    builder = InlineKeyboardBuilder()
    text_dict = texts.get(language, texts['ru'])
    
    builder.button(text=text_dict['yes'], callback_data="confirm_yes")
    builder.button(text=text_dict['no'], callback_data="confirm_no")
    builder.adjust(2)
    
    return builder.as_markup()
