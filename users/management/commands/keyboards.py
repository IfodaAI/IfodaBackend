from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, ReplyKeyboardMarkup, KeyboardButton
from django.conf import settings

from users.management.commands import bot


def get_webapp_inline_keyboard() -> InlineKeyboardMarkup:
    """WebApp tugmasini qaytaradi"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🏪 Ifoda Shop'ни очиш:",
                    web_app=WebAppInfo(url=settings.WEBAPP_URL)
                )
            ]
        ]
    )


def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Asosiy menyu tugmalarini qaytaradi"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=bot.BUTTONS["online_agronom"])],
            [KeyboardButton(text=bot.BUTTONS["nearest_branches"]), KeyboardButton(text=bot.BUTTONS["help"])],
            [KeyboardButton(text=bot.BUTTONS["change_language"]), KeyboardButton(text=bot.BUTTONS["about_us"])],
        ],
        resize_keyboard=True,
    )