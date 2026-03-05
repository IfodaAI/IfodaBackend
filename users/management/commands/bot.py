import asyncio
import logging
import re
import warnings
from contextlib import suppress

from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import transaction
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    WebAppInfo,
)
from asgiref.sync import sync_to_async

from users.management.commands.keyboards import get_main_keyboard
from users.models import User, TelegramUser
from users.management.commands.broadcast import router as broadcast_router

# Suppress pydantic warnings
warnings.filterwarnings(
    "ignore",
    message="Field name .* shadows an attribute in parent .*",
    module="pydantic",
)

# ============== CONSTANTS ==============
MESSAGES = {
    "welcome_back": "*Хуш келибсиз, {name}!*\n",
    "open_app": "Иловани очиш учун қуйидаги тугмани босинг:",
    "welcome_new": "*Ifoda Shop*га хуш келибсиз!\nИлтимос, телефон рақамингизни улашинг ёки қўлда киритинг:",
    "registration_success": "*Рўйхатдан ўтганингиз учун раҳмат!*",
    "app_ready": "Энди иловани ишлатишингиз мумкин:",
    "registration_error": "Рўйхатдан ўтишда хатолик юз берди. Илтимос, қайта уриниб кўринг.",
    "enter_phone": "*Илтимос, телефон рақамингизни* қуйидаги форматда юборинг:\n`+998901234567`",
    "invalid_phone": "Нотўғри формат. Илтимос, рақамни +998901234567 форматида киритинг",
}

BUTTONS = {
    "open_shop": "🏪 Ifoda Shop",
    "online_agronom": "🌱 Онлайн Агроном",
    "nearest_branches": "📍 Яқин атрофдаги филиалларимиз",
    "help": "❓ Ёрдам",
    "change_language": "🌐 Тилни танлаш",
    "about_us": "ℹ️ Биз ҳақимизда",
    "share_contact": "Рақамни улашиш 📞",
    "manual_input": "Қўлда киритиш ✍️",
    "start_command": "Ботни ишга тушириш 🚀",
}

PHONE_REGEX = re.compile(r"^\+998[0-9]{9}$")

# Initialize dispatcher
dp = Dispatcher()
dp.include_router(broadcast_router)


# ============== HELPER FUNCTIONS ==============


def get_registration_keyboard() -> ReplyKeyboardMarkup:
    """Ro'yxatdan o'tish tugmalarini qaytaradi"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=BUTTONS["share_contact"], request_contact=True),
                KeyboardButton(text=BUTTONS["manual_input"]),
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )


def is_valid_phone(phone: str) -> bool:
    """Telefon raqamini tekshiradi"""
    return bool(PHONE_REGEX.match(phone))


@sync_to_async
def register_user(telegram_id: int, phone_number: str, first_name: str) -> TelegramUser:
    """Foydalanuvchini ro'yxatdan o'tkazadi (transaction bilan)"""
    with transaction.atomic():
        base_user = User.objects.create_user(
            phone_number=phone_number,
            telegram_id=telegram_id,
            first_name=first_name,
            role="USER",
        )
        user, _ = TelegramUser.objects.get_or_create(
            telegram_id=telegram_id,
            defaults={
                "phone_number": phone_number,
                "first_name": first_name,
                "user": base_user
            }
        )
        return user


async def send_success_response(message: types.Message) -> None:
    """Muvaffaqiyatli ro'yxatdan o'tish xabarlarini yuboradi"""
    await message.answer(
        MESSAGES["registration_success"],
        reply_markup=get_main_keyboard(),
        parse_mode=ParseMode.MARKDOWN
    )


async def send_error_response(message: types.Message, error: Exception, handler_name: str) -> None:
    """Xatolik xabarini yuboradi va log qiladi"""
    await message.answer(MESSAGES["registration_error"])
    logging.error(f"Error in {handler_name}: {error}")


# ============== HANDLERS ==============
@dp.message(CommandStart())
async def start_handler(message: types.Message):
    """Start komandasi handleri"""
    user = await sync_to_async(
        TelegramUser.objects.filter(telegram_id=message.from_user.id).first
    )()

    if user:
        await message.answer(
            MESSAGES["welcome_back"].format(name=user.first_name),
            reply_markup=get_main_keyboard(),
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        await message.answer(
            MESSAGES["welcome_new"],
            reply_markup=get_registration_keyboard(),
            parse_mode=ParseMode.MARKDOWN
        )


@dp.message(lambda msg: msg.contact is not None)
async def contact_handler(message: types.Message):
    """Kontakt orqali ro'yxatdan o'tish"""
    try:
        contact = message.contact
        await register_user(
            telegram_id=message.from_user.id,
            phone_number=contact.phone_number,
            first_name=contact.first_name or message.from_user.first_name
        )
        await send_success_response(message)
    except Exception as e:
        await send_error_response(message, e, "contact_handler")


@dp.message(lambda msg: msg.text == BUTTONS["manual_input"])
async def manual_registration(message: types.Message):
    """Qo'lda kiritish tugmasi bosilganda"""
    await message.answer(
        MESSAGES["enter_phone"],
        parse_mode=ParseMode.MARKDOWN
    )


@dp.message(lambda msg: msg.text and msg.text.startswith("+998"))
async def handle_phone_manual(message: types.Message):
    """Qo'lda telefon raqami kiritilganda"""
    phone_number = message.text.strip()

    if not is_valid_phone(phone_number):
        await message.answer(MESSAGES["invalid_phone"])
        return

    try:
        await register_user(
            telegram_id=message.from_user.id,
            phone_number=phone_number,
            first_name=message.from_user.first_name
        )
        await send_success_response(message)
    except Exception as e:
        await send_error_response(message, e, "handle_phone_manual")


# ============== COMMAND ==============
class Command(BaseCommand):
    help = "Starts the Telegram bot in polling mode"

    async def shutdown(self, dispatcher: Dispatcher, bot: Bot):
        """Graceful shutdown"""
        self.stdout.write(self.style.WARNING("\nShutting down..."))
        await bot.session.close()
        await dispatcher.stop_polling()

    async def handle_async(self, *args, **options):
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler("bot.log")
            ]
        )

        bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
        await bot.set_my_commands([
            types.BotCommand(command="start", description=BUTTONS["start_command"]),
            types.BotCommand(command="admin", description="Admin panel"),
        ])

        self.stdout.write(
            self.style.SUCCESS("Bot started in polling mode...\nPress Ctrl+C to stop")
        )

        try:
            await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Bot stopped with error: {e}"))
            logging.error(f"Bot error: {e}")
        finally:
            with suppress(Exception):
                await self.shutdown(dp, bot)

    def handle(self, *args, **options):
        try:
            asyncio.run(self.handle_async(*args, **options))
        except KeyboardInterrupt:
            self.stdout.write(self.style.SUCCESS("\nBot stopped successfully!"))
