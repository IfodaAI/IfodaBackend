# yourapp/management/commands/send_broadcast.py

import asyncio
import csv
from django.core.management.base import BaseCommand
from aiogram import Bot


class Command(BaseCommand):
    help = 'CSV fayldan telegram IDlarni olib barcha foydalanuvchilarga xabar yuborish'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='CSV fayl yoli')
        parser.add_argument('message', type=str, help='Yuboriladigan xabar')

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        message = options['message']

        # CSV dan IDlarni olish
        user_ids = []
        with open(csv_file, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if row:
                    user_ids.append(int(row[0]))

        self.stdout.write(f"Jami foydalanuvchilar: {len(user_ids)}")

        asyncio.run(self.send_messages(user_ids, message))

    async def send_messages(self, user_ids, message):
        from django.conf import settings
        bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)

        success, failed = 0, 0

        for user_id in user_ids:
            try:
                await bot.send_message(chat_id=user_id, text=message)
                success += 1
                await asyncio.sleep(0.05)  # 20 msg/sec
            except Exception as e:
                self.stdout.write(f"Xato {user_id}: {e}")
                failed += 1

        await bot.session.close()
        self.stdout.write(self.style.SUCCESS(f"✅ Yuborildi: {success} | ❌ Xato: {failed}"))