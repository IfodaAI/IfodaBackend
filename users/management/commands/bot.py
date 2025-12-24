from django.core.management.base import BaseCommand
from django.conf import settings
import asyncio
import logging
import warnings
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    WebAppInfo,
    ReplyKeyboardRemove
)
from users.models import TelegramUser
from asgiref.sync import sync_to_async

# Suppress pydantic warnings
warnings.filterwarnings(
    "ignore",
    message="Field name .* shadows an attribute in parent .*",
    module="pydantic",
)

# Initialize dispatcher
dp = Dispatcher()

@dp.message(CommandStart())
async def start_handler(message: types.Message):
    # Check if user already exists
    user = await sync_to_async(TelegramUser.objects.filter(telegram_id=str(message.from_user.id)).first)()
    
    if user:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🏪 Ifoda Shop'ni ochish", 
                        web_app=WebAppInfo(url=settings.WEBAPP_URL)
                    )
                ]
            ]
        )
        # Remove previous keyboard and send new message
        await message.answer(
            f"*Xush kelibsiz, {user.first_name}!*\nIlovani ishlatishingiz mumkin:",
            reply_markup=types.ReplyKeyboardRemove(),  # Remove keyboard
            parse_mode=ParseMode.MARKDOWN
        )
        # Send webapp button separately
        await message.answer(
            "Ilovani ochish uchun quyidagi tugmani bosing:",
            reply_markup=keyboard,
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="Raqamni ulashish 📞", request_contact=True),
                    KeyboardButton(text="Qo'lda kiritish ✍️"),
                ]
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        await message.answer(
            "*Ifoda Shop*ga xush kelibsiz!\nIltimos, telefon raqamingizni ulashing yoki qo'lda kiriting:", 
            reply_markup=keyboard,
            parse_mode=ParseMode.MARKDOWN
        )

@dp.message(lambda msg: msg.contact is not None)
async def contact_handler(message: types.Message):
    try:
        contact = message.contact
        user, created = await sync_to_async(TelegramUser.objects.get_or_create)(
            telegram_id=str(message.from_user.id),
            defaults={
                "phone_number": contact.phone_number,
                "first_name": contact.first_name or message.from_user.first_name,
            },
        )
        
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🏪 Ifoda Shop'ni ochish", 
                        web_app=WebAppInfo(url=settings.WEBAPP_URL)
                    )
                ]
            ]
        )

        await message.answer(
            "*Ro'yxatdan o'tganingiz uchun rahmat!*",
            reply_markup=ReplyKeyboardRemove,
            parse_mode=ParseMode.MARKDOWN
        )
        
        await message.answer(
            "Endi ilovani ishlatishingiz mumkin:",
            reply_markup=keyboard,
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        await message.answer("Ro'yxatdan o'tishda xatolik yuz berdi. Iltimos, qayta urinib ko'ring.")
        logging.error(f"Error in contact_handler: {e}")

@dp.message(lambda msg: msg.text == "Qo'lda kiritish ✍️")
async def manual_registration(message: types.Message):
    await message.answer(
        "*Iltimos, telefon raqamingizni* quyidagi formatda yuboring:\n`+998901234567`",
        parse_mode=ParseMode.MARKDOWN
    )

@dp.message(lambda msg: msg.text and msg.text.startswith("+998"))
async def handle_phone_manual(message: types.Message):
    try:
        phone_number = message.text.strip()
        if len(phone_number) != 13:
            await message.answer("Noto'g'ri format. Iltimos, raqamni +998901234567 formatida kiriting")
            return

        user, created = await sync_to_async(TelegramUser.objects.get_or_create)(
            telegram_id=str(message.from_user.id),
            defaults={
                "phone_number": phone_number,
                "first_name": message.from_user.first_name,
            },
        )
        
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🏪 Ifoda Shop'ni ochish", 
                        web_app=WebAppInfo(url=settings.WEBAPP_URL)
                    )
                ]
            ]
        )
        
        await message.answer(
            "*Ro'yxatdan o'tganingiz uchun rahmat!*",
            reply_markup=ReplyKeyboardRemove,
            parse_mode=ParseMode.MARKDOWN
        )
        await message.answer(
            "Endi ilovani ishlatishingiz mumkin:",
            reply_markup=keyboard,
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        await message.answer("Ro'yxatdan o'tishda xatolik yuz berdi. Iltimos, qayta urinib ko'ring.")
        logging.error(f"Error in handle_phone_manual: {e}")

import signal
from contextlib import suppress
from aiogram.exceptions import TelegramAPIError

class Command(BaseCommand):
    help = "Starts the Telegram bot in polling mode"

    async def shutdown(self, dispatcher: Dispatcher, bot: Bot):
        """Graceful shutdown"""
        self.stdout.write(self.style.WARNING("\nShutting down..."))
        
        # Close bot instance
        await bot.session.close()
        
        # Close dispatcher
        await dispatcher.stop_polling()

    async def handle_async(self, *args, **options):
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler("bot.log")
            ]
        )

        # Initialize bot
        bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
        
        self.stdout.write(
            self.style.SUCCESS("Bot started in polling mode...\nPress Ctrl+C to stop")
        )
        
        try:
            # Start polling
            await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Bot stopped with error: {e}")
            )
            logging.error(f"Bot error: {e}")
            
        finally:
            with suppress(Exception):
                await self.shutdown(dp, bot)

    def handle(self, *args, **options):
        try:
            asyncio.run(self.handle_async(*args, **options))
        except KeyboardInterrupt:
            self.stdout.write(self.style.SUCCESS("\nBot stopped successfully!"))