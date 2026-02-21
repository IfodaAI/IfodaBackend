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
    WebAppInfo
)
from users.models import User,TelegramUser
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
                        text="🏪 Ifoda Shopни очиш",
                        web_app=WebAppInfo(url=settings.WEBAPP_URL)
                    )
                ]
            ]
        )
        # Remove previous keyboard and send new message
        await message.answer(
            f"*Хуш келибсиз, {user.first_name}!*\nИловани ишлатишингиз мумкин:",
            reply_markup=types.ReplyKeyboardRemove(),  # Remove keyboard
            parse_mode=ParseMode.MARKDOWN
        )
        # Send webapp button separately
        await message.answer(
            "Иловани очиш учун қуйидаги тугмани босинг:",
            reply_markup=keyboard,
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="Рақамни улашиш 📞", request_contact=True),
                    KeyboardButton(text="Қўлда киритиш ✍️"),
                ]
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        await message.answer(
            "*Ifoda Shop*га хуш келибсиз!\nИлтимос, телефон рақамингизни улашинг ёки қўлда киритинг:", 
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
                        text="🏪 Ifoda Shopни очиш",
                        web_app=WebAppInfo(url=settings.WEBAPP_URL)
                    )
                ]
            ]
        )

        await message.answer(
            "*Рўйхатдан ўтганингиз учун раҳмат!*",
            reply_markup=types.ReplyKeyboardRemove(),
            parse_mode=ParseMode.MARKDOWN
        )
        
        await message.answer(
            "Энди иловани ишлатишингиз мумкин:",
            reply_markup=keyboard,
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        await message.answer("Рўйхатдан ўтишда хатолик юз берди. Илтимос, қайта уриниб кўринг.")
        logging.error(f"Error in contact_handler: {e}")

@dp.message(lambda msg: msg.text == "Қўлда киритиш ✍️")
async def manual_registration(message: types.Message):
    await message.answer(
        "*Илтимос, телефон рақамингизни* қуйидаги форматда юборинг:\n`+998901234567`",
        parse_mode=ParseMode.MARKDOWN
    )

@dp.message(lambda msg: msg.text and msg.text.startswith("+998"))
async def handle_phone_manual(message: types.Message):
    try:
        phone_number = message.text.strip()
        if len(phone_number) != 13:
            await message.answer("Нотўғри формат. Илтимос, рақамни +998901234567 форматида киритинг")
            return
        
        base_user, created = await sync_to_async(User.objects.create_user_with_random_password)(
            telegram_id=message.from_user.id,
            phone_number=phone_number,
            first_name=message.from_user.first_name
        )

        user, created = await sync_to_async(TelegramUser.objects.get_or_create)(
            telegram_id=message.from_user.id,
            defaults={
                "phone_number": phone_number,
                "first_name": message.from_user.first_name,
                "user":base_user
            },
        )
        
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🏪 Ifoda Shopни очиш",
                        web_app=WebAppInfo(url=settings.WEBAPP_URL)
                    )
                ]
            ]
        )
        
        await message.answer(
            "*Рўйхатдан ўтганингиз учун раҳмат!*",
            reply_markup=types.ReplyKeyboardRemove(),
            parse_mode=ParseMode.MARKDOWN
        )
        await message.answer(
            "Энди иловани ишлатишингиз мумкин:",
            reply_markup=keyboard,
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        await message.answer("Рўйхатдан ўтишда хатолик юз берди. Илтимос, қайта уриниб кўринг.")
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