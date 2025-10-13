import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from users.models import Region, District  # <-- models joylashgan app nomi to‘g‘ri

# Avval eski District ma'lumotlarini tozalaymiz
District.objects.all().delete()
Region.objects.all().delete()

print("🧹 Eski region va district ma'lumotlari o‘chirildi...")

regions = {
    "Toshkent shahri": [
        "Bektemir tumani", "Chilonzor tumani", "Mirzo Ulug‘bek tumani", "Mirobod tumani",
        "Olmazor tumani", "Sergeli tumani", "Shayxontohur tumani", "Uchtepa tumani",
        "Yakkasaroy tumani", "Yashnobod tumani", "Yunusobod tumani"
    ],
    "Toshkent viloyati": [
        "Toshkent shahri", "Angren shahri", "Bekobod shahri", "Ohangaron shahri", "Chirchiq shahri",
        "Yangiyo‘l shahri", "Bekobod tumani", "Bo‘ka tumani", "Chinoz tumani", "Ohangaron tumani",
        "Parkent tumani", "Piskent tumani", "Quyi Chirchiq tumani", "Oqqo‘rg‘on tumani",
        "Qibray tumani", "Zangiota tumani", "Yuqori Chirchiq tumani"
    ],
    "Andijon viloyati": [
        "Andijon shahri", "Asaka shahri", "Xonobod shahri",
        "Andijon tumani", "Asaka tumani", "Baliqchi tumani", "Bo‘z tumani", "Bulakbashi tumani",
        "Izboskan tumani", "Jalaquduq tumani", "Marhamat tumani", "Oltinko‘l tumani",
        "Paxtaobod tumani", "Qo‘rg‘ontepa tumani", "Shahrixon tumani", "Xo‘jaobod tumani", "Ulug‘nor tumani"
    ],
    "Namangan viloyati": [
        "Namangan shahri", "Namangan tumani", "Chortoq tumani", "Chust tumani", "Kosonsoy tumani",
        "Mingbuloq tumani", "Norin tumani", "Pop tumani", "To‘raqo‘rg‘on tumani", "Uychi tumani", "Yangiqo‘rg‘on tumani"
    ],
    "Farg‘ona viloyati": [
        "Farg‘ona shahri", "Qo‘qon shahri", "Marg‘ilon shahri",
        "Oltiariq tumani", "Bag‘dod tumani", "Beshariq tumani", "Dang‘ara tumani", "Furqat tumani",
        "Quva tumani", "Rishton tumani", "So‘x tumani", "Toshloq tumani", "Uchko‘prik tumani", "Yozyovon tumani"
    ],
    "Sirdaryo viloyati": [
        "Guliston shahri", "Yangiyer shahri", "Shirin shahri",
        "Boyovut tumani", "Mirzaobod tumani", "Oqoltin tumani", "Sayxunobod tumani",
        "Sardoba tumani", "Sirdaryo tumani", "Xovos tumani"
    ],
    "Jizzax viloyati": [
        "Jizzax shahri",
        "Arnasoy tumani", "Baxmal tumani", "Do‘stlik tumani", "Forish tumani",
        "G‘allaorol tumani", "Mirzacho‘l tumani", "Paxtakor tumani", "Yangiobod tumani",
        "Zafarobod tumani", "Zarbdor tumani", "Zomin tumani"
    ],
    "Samarqand viloyati": [
        "Samarqand shahri", "Kattaqo‘rg‘on shahri",
        "Bulung‘ur tumani", "Ishtixon tumani", "Jomboy tumani", "Narpay tumani",
        "Nurobod tumani", "Oqdaryo tumani", "Paxtachi tumani", "Payariq tumani",
        "Pastdarg‘om tumani", "Tayloq tumani", "Urgut tumani"
    ],
    "Qashqadaryo viloyati": [
        "Qarshi shahri", "Shahrisabz shahri",
        "Dehqonobod tumani", "G‘uzor tumani", "Kasbi tumani", "Kitob tumani", "Koson tumani",
        "Mirishkor tumani", "Muborak tumani", "Nishon tumani", "Yakkabog‘ tumani", "Chiroqchi tumani"
    ],
    "Surxondaryo viloyati": [
        "Termiz shahri", "Denov shahri",
        "Angor tumani", "Bandixon tumani", "Boysun tumani", "Jarqo‘rg‘on tumani",
        "Muzrabot tumani", "Oltinsoy tumani", "Qiziriq tumani", "Qumqo‘rg‘on tumani",
        "Sariosiyo tumani", "Sherobod tumani", "Sho‘rchi tumani"
    ],
    "Navoiy viloyati": [
        "Navoiy shahri", "Zarafshon shahri", "Uchquduq shahri",
        "Karmana tumani", "Konimex tumani", "Navbahor tumani", "Nurota tumani",
        "Qiziltepa tumani", "Tomdi tumani", "Xatirchi tumani"
    ],
    "Buxoro viloyati": [
        "Buxoro shahri", "Kogon shahri",
        "G‘ijduvon tumani", "Jondor tumani", "Olot tumani", "Peshku tumani",
        "Qorako‘l tumani", "Qorovulbozor tumani", "Romitan tumani", "Shofirkon tumani", "Vobkent tumani"
    ],
    "Xorazm viloyati": [
        "Urganch shahri", "Xiva shahri",
        "Bog‘ot tumani", "Gurlan tumani", "Xonqa tumani", "Hazorasp tumani",
        "Qo‘shko‘pir tumani", "Shovot tumani", "Yangiariq tumani", "Yangibozor tumani"
    ],
    "Qoraqalpog‘iston Respublikasi": [
        "Nukus shahri", "Taxiatosh shahri",
        "Amudaryo tumani", "Beruniy tumani", "Chimboy tumani", "Ellikqal‘a tumani",
        "Kegeyli tumani", "Mo‘ynoq tumani", "Qanliko‘l tumani", "Qorao‘zak tumani",
        "Qo‘ng‘irot tumani", "Shumanay tumani", "Taxtako‘pir tumani", "To‘rtko‘l tumani", "Xo‘jayli tumani"
    ]
}

for region_name, districts in regions.items():
    region, _ = Region.objects.get_or_create(name=region_name)
    for district_name in districts:
        District.objects.get_or_create(name=district_name, region=region)

print("✅ Barcha region va district ma'lumotlari bazaga muvaffaqiyatli kiritildi!")

"""
1.Begona O't
2.Zararkunanda
3.Kasallik
4.Ozuqa yetishmasligi
"""