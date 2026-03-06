import asyncio
import logging

from aiogram import Bot, Router, types, F
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from asgiref.sync import sync_to_async

from django.conf import settings

from users.management.commands.keyboards import get_webapp_inline_keyboard
from users.models import User, TelegramUser, Region

logger = logging.getLogger(__name__)

router = Router()


# ============== FSM STATES ==============
class BroadcastStates(StatesGroup):
    choosing_audience = State()
    choosing_region = State()
    waiting_content = State()
    confirming = State()


# ============== CONSTANTS ==============
AUDIENCE_ALL = "audience_all"
AUDIENCE_ACTIVE = "audience_active"
AUDIENCE_REGION = "audience_region"

CONFIRM_YES = "broadcast_confirm_yes"
CONFIRM_NO = "broadcast_confirm_no"
CANCEL = "broadcast_cancel"


# ============== HELPER FUNCTIONS ==============
@sync_to_async
def is_admin(telegram_id: int) -> bool:
    """Admin tekshiruvi: TG_ADMINS_BROADCAST ro'yxati + bazadan role tekshirish"""
    admin_ids = getattr(settings, "TG_ADMINS_BROADCAST", [])
    if str(telegram_id) in admin_ids:
        return True
    return User.objects.filter(telegram_id=telegram_id, role="ADMIN").exists()


@sync_to_async
def get_recipients(audience: str, region_id: str = None) -> list[int]:
    """Auditoriyaga qarab telegram_id lar ro'yxatini qaytaradi"""
    if audience == AUDIENCE_ALL:
        return list(
            TelegramUser.objects.exclude(telegram_id__isnull=True)
            .values_list("telegram_id", flat=True)
        )
    elif audience == AUDIENCE_ACTIVE:
        active_user_tg_ids = User.objects.filter(
            is_active=True, telegram_id__isnull=False
        ).values_list("telegram_id", flat=True)
        return list(active_user_tg_ids)
    elif audience == AUDIENCE_REGION and region_id:
        return list(
            TelegramUser.objects.filter(region_id=region_id)
            .exclude(telegram_id__isnull=True)
            .values_list("telegram_id", flat=True)
        )
    return []


@sync_to_async
def get_recipient_count(audience: str, region_id: str = None) -> int:
    """Qabul qiluvchilar sonini qaytaradi"""
    if audience == AUDIENCE_ALL:
        return TelegramUser.objects.exclude(telegram_id__isnull=True).count()
    elif audience == AUDIENCE_ACTIVE:
        return User.objects.filter(
            is_active=True, telegram_id__isnull=False
        ).count()
    elif audience == AUDIENCE_REGION and region_id:
        return TelegramUser.objects.filter(
            region_id=region_id
        ).exclude(telegram_id__isnull=True).count()
    return 0


@sync_to_async
def get_regions() -> list[dict]:
    """Regionlar ro'yxatini qaytaradi"""
    return list(Region.objects.values("id", "name"))


def get_audience_keyboard() -> InlineKeyboardMarkup:
    """Auditoriya tanlash tugmalari"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📢 Barchaga", callback_data=AUDIENCE_ALL)],
            [InlineKeyboardButton(text="✅ Faqat active", callback_data=AUDIENCE_ACTIVE)],
            [InlineKeyboardButton(text="🗺 Region bo'yicha", callback_data=AUDIENCE_REGION)],
            [InlineKeyboardButton(text="❌ Bekor qilish", callback_data=CANCEL)],
        ]
    )


def get_confirm_keyboard() -> InlineKeyboardMarkup:
    """Tasdiqlash tugmalari"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Ha, yuborish", callback_data=CONFIRM_YES),
                InlineKeyboardButton(text="❌ Bekor qilish", callback_data=CONFIRM_NO),
            ]
        ]
    )


def extract_inline_keyboard(message: types.Message) -> dict | None:
    """Xabardagi inline buttonlarni dict formatida olish"""
    if not message.reply_markup or not isinstance(
        message.reply_markup, InlineKeyboardMarkup
    ):
        return None
    rows = []
    for row in message.reply_markup.inline_keyboard:
        buttons = []
        for btn in row:
            button_data = {"text": btn.text}
            if btn.url:
                button_data["url"] = btn.url
            elif btn.web_app:
                button_data["web_app_url"] = btn.web_app.url
            else:
                # callback_data va boshqa turlar broadcast uchun yaroqsiz
                continue
            buttons.append(button_data)
        if buttons:
            rows.append(buttons)
    return rows if rows else None


def build_inline_keyboard(rows: list[list[dict]]) -> InlineKeyboardMarkup:
    """Saqlangan button ma'lumotlaridan InlineKeyboardMarkup yaratish"""
    keyboard = []
    for row in rows:
        kb_row = []
        for btn in row:
            if "url" in btn:
                kb_row.append(InlineKeyboardButton(text=btn["text"], url=btn["url"]))
            elif "web_app_url" in btn:
                kb_row.append(InlineKeyboardButton(
                    text=btn["text"],
                    web_app=types.WebAppInfo(url=btn["web_app_url"]),
                ))
        if kb_row:
            keyboard.append(kb_row)
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


async def broadcast_to_users(
    bot: Bot, recipients: list[int], content: dict
) -> tuple[int, int]:
    """
    Foydalanuvchilarga xabar yuboradi.
    Returns: (success_count, fail_count)
    """
    success = 0
    fail = 0
    content_type = content["type"]

    # Inline button mavjud bo'lsa reply_markup yaratish
    reply_markup = None
    if content.get("buttons"):
        reply_markup = build_inline_keyboard(content["buttons"])

    for chat_id in recipients:
        try:
            if content_type == "text":
                await bot.send_message(
                    chat_id=chat_id,
                    text=content["text"],
                    parse_mode=ParseMode.HTML,
                    reply_markup=reply_markup,
                )
            elif content_type == "photo":
                await bot.send_photo(
                    chat_id=chat_id,
                    photo=content["file_id"],
                    caption=content.get("caption"),
                    parse_mode=ParseMode.HTML,
                    reply_markup=reply_markup,
                )
            elif content_type == "video":
                await bot.send_video(
                    chat_id=chat_id,
                    video=content["file_id"],
                    caption=content.get("caption"),
                    parse_mode=ParseMode.HTML,
                    reply_markup=reply_markup,
                )
            success += 1
        except Exception as e:
            fail += 1
            logger.warning(f"Broadcast xatolik chat_id={chat_id}: {e}")

        # Telegram rate limit: 30 xabar/soniya
        await asyncio.sleep(0.05)

    return success, fail


# ============== HANDLERS ==============
@router.message(Command("admin"))
async def admin_handler(message: types.Message, state: FSMContext):
    """/admin buyrug'i — admin tekshiruv va auditoriya tanlash"""
    if not await is_admin(message.from_user.id):
        await message.answer("⛔ Sizda bu buyruqdan foydalanish huquqi yo'q.")
        return

    await state.clear()
    await message.answer(
        "📢 <b>Broadcast xabar yuborish</b>\n\nAuditoriyani tanlang:",
        reply_markup=get_audience_keyboard(),
        parse_mode=ParseMode.HTML,
    )
    await state.set_state(BroadcastStates.choosing_audience)


@router.callback_query(BroadcastStates.choosing_audience, F.data == CANCEL)
async def cancel_broadcast(callback: CallbackQuery, state: FSMContext):
    """Broadcast bekor qilish"""
    await state.clear()
    await callback.message.edit_text("❌ Broadcast bekor qilindi.")
    await callback.answer()


@router.callback_query(
    BroadcastStates.choosing_audience, F.data.in_({AUDIENCE_ALL, AUDIENCE_ACTIVE})
)
async def audience_selected(callback: CallbackQuery, state: FSMContext):
    """Barcha yoki active auditoriya tanlanganda"""
    audience = callback.data
    count = await get_recipient_count(audience)

    label = "barcha" if audience == AUDIENCE_ALL else "active"
    await state.update_data(audience=audience)

    await callback.message.edit_text(
        f"👥 <b>{label.capitalize()} foydalanuvchilar:</b> {count} ta\n\n"
        "Endi xabar kontentini yuboring:\n"
        "• Matn yozing\n"
        "• Rasm yuboring\n"
        "• Video yuboring",
        parse_mode=ParseMode.HTML,
    )
    await state.set_state(BroadcastStates.waiting_content)
    await callback.answer()


@router.callback_query(BroadcastStates.choosing_audience, F.data == AUDIENCE_REGION)
async def region_audience_selected(callback: CallbackQuery, state: FSMContext):
    """Region bo'yicha auditoriya tanlanganda — regionlar ro'yxatini ko'rsatish"""
    regions = await get_regions()
    if not regions:
        await callback.message.edit_text("❌ Regionlar topilmadi.")
        await state.clear()
        await callback.answer()
        return

    buttons = [
        [InlineKeyboardButton(
            text=r["name"],
            callback_data=f"region_{r['id']}",
        )]
        for r in regions
    ]
    buttons.append([InlineKeyboardButton(text="❌ Bekor qilish", callback_data=CANCEL)])

    await callback.message.edit_text(
        "🗺 <b>Regionni tanlang:</b>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
        parse_mode=ParseMode.HTML,
    )
    await state.set_state(BroadcastStates.choosing_region)
    await callback.answer()


@router.callback_query(BroadcastStates.choosing_region, F.data == CANCEL)
async def cancel_region(callback: CallbackQuery, state: FSMContext):
    """Region tanlash bosqichida bekor qilish"""
    await state.clear()
    await callback.message.edit_text("❌ Broadcast bekor qilindi.")
    await callback.answer()


@router.callback_query(BroadcastStates.choosing_region, F.data.startswith("region_"))
async def region_chosen(callback: CallbackQuery, state: FSMContext):
    """Region tanlanganda"""
    region_id = callback.data.split("_", 1)[1]
    count = await get_recipient_count(AUDIENCE_REGION, region_id)

    await state.update_data(audience=AUDIENCE_REGION, region_id=region_id)

    await callback.message.edit_text(
        f"🗺 <b>Tanlangan region:</b> {count} ta foydalanuvchi\n\n"
        "Endi xabar kontentini yuboring:\n"
        "• Matn yozing\n"
        "• Rasm yuboring\n"
        "• Video yuboring",
        parse_mode=ParseMode.HTML,
    )
    await state.set_state(BroadcastStates.waiting_content)
    await callback.answer()


@router.message(BroadcastStates.waiting_content, F.text)
async def receive_text_content(message: types.Message, state: FSMContext):
    """Matnli kontent qabul qilish"""
    data = await state.get_data()
    audience = data["audience"]
    region_id = data.get("region_id")
    count = await get_recipient_count(audience, region_id)

    buttons = extract_inline_keyboard(message)
    content = {"type": "text", "text": message.text}
    if buttons:
        content["buttons"] = buttons

    await state.update_data(content=content)

    btn_info = "🔘 Button: Ha\n" if buttons else ""
    await message.answer(
        f"📋 <b>Tasdiqlash</b>\n\n"
        f"📝 Turi: Matn\n"
        f"{btn_info}"
        f"👥 Qabul qiluvchilar: {count} ta\n\n"
        f"Yuborilsinmi?",
        reply_markup=get_confirm_keyboard(),
        parse_mode=ParseMode.HTML,
    )
    await state.set_state(BroadcastStates.confirming)


@router.message(BroadcastStates.waiting_content, F.photo)
async def receive_photo_content(message: types.Message, state: FSMContext):
    """Rasmli kontent qabul qilish"""
    data = await state.get_data()
    audience = data["audience"]
    region_id = data.get("region_id")
    count = await get_recipient_count(audience, region_id)

    file_id = message.photo[-1].file_id
    caption = message.caption or ""
    buttons = extract_inline_keyboard(message)

    content = {"type": "photo", "file_id": file_id, "caption": caption}
    if buttons:
        content["buttons"] = buttons

    await state.update_data(content=content)

    btn_info = "🔘 Button: Ha\n" if buttons else ""
    await message.answer(
        f"📋 <b>Tasdiqlash</b>\n\n"
        f"🖼 Turi: Rasm\n"
        f"{btn_info}"
        f"👥 Qabul qiluvchilar: {count} ta\n\n"
        f"Yuborilsinmi?",
        reply_markup=get_confirm_keyboard(),
        parse_mode=ParseMode.HTML,
    )
    await state.set_state(BroadcastStates.confirming)


@router.message(BroadcastStates.waiting_content, F.video)
async def receive_video_content(message: types.Message, state: FSMContext):
    """Videoli kontent qabul qilish"""
    data = await state.get_data()
    audience = data["audience"]
    region_id = data.get("region_id")
    count = await get_recipient_count(audience, region_id)

    file_id = message.video.file_id
    caption = message.caption or ""
    buttons = extract_inline_keyboard(message)

    content = {"type": "video", "file_id": file_id, "caption": caption}
    if buttons:
        content["buttons"] = buttons

    await state.update_data(content=content)

    btn_info = "🔘 Button: Ha\n" if buttons else ""
    await message.answer(
        f"📋 <b>Tasdiqlash</b>\n\n"
        f"🎬 Turi: Video\n"
        f"{btn_info}"
        f"👥 Qabul qiluvchilar: {count} ta\n\n"
        f"Yuborilsinmi?",
        reply_markup=get_confirm_keyboard(),
        parse_mode=ParseMode.HTML,
    )
    await state.set_state(BroadcastStates.confirming)


@router.message(BroadcastStates.waiting_content)
async def receive_unsupported_content(message: types.Message, state: FSMContext):
    """Qo'llab-quvvatlanmaydigan kontent turi"""
    await message.answer(
        "⚠️ Faqat matn, rasm yoki video qabul qilinadi. Qayta yuboring.",
    )


@router.callback_query(BroadcastStates.confirming, F.data == CONFIRM_NO)
async def broadcast_cancelled(callback: CallbackQuery, state: FSMContext):
    """Broadcast rad etildi"""
    await state.clear()
    await callback.message.edit_text("❌ Broadcast bekor qilindi.")
    await callback.answer()


@router.callback_query(BroadcastStates.confirming, F.data == CONFIRM_YES)
async def broadcast_confirmed(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """Broadcast tasdiqlandi — yuborishni boshlash"""
    data = await state.get_data()
    audience = data["audience"]
    region_id = data.get("region_id")
    content = data["content"]

    await callback.message.edit_text("⏳ Xabarlar yuborilmoqda...")
    await callback.answer()

    recipients = await get_recipients(audience, region_id)

    if not recipients:
        await callback.message.edit_text("❌ Qabul qiluvchilar topilmadi.")
        await state.clear()
        return

    success, fail = await broadcast_to_users(bot, recipients, content)

    await callback.message.edit_text(
        f"✅ <b>Broadcast yakunlandi!</b>\n\n"
        f"📨 Yuborildi: {success}\n"
        f"❌ Xatolik: {fail}\n"
        f"📊 Jami: {success + fail}",
        parse_mode=ParseMode.HTML,
    )
    await state.clear()


@router.message(F.text == "🌱 Онлайн Агроном")
async def send_user_web_app(message: types.Message):
    await message.answer(
        "Иловани ишлатишингиз мумкин:",
        reply_markup=get_webapp_inline_keyboard(),
        parse_mode=ParseMode.MARKDOWN,
    )



