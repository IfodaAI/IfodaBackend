import json
import math


def parse_ids_param(ids_param: str) -> list:
    """
    IDs parametrini parse qiladi.
    Qo'llab-quvvatlanadigan formatlar:
    - ids=[1,2,3] (JSON array)
    - ids=1,2,3 (vergul bilan ajratilgan)

    Args:
        ids_param: IDs string parametri

    Returns:
        IDs ro'yxati
    """
    if not ids_param:
        return []

    try:
        # JSON format: [1,2,3]
        return json.loads(ids_param)
    except json.JSONDecodeError:
        # Vergul bilan ajratilgan: 1,2,3
        return [id_str.strip() for id_str in ids_param.split(",") if id_str.strip()]


def get_distance_from_lat_lon_in_km(lat1, lon1, lat2, lon2):
    """
    lat1-user latitude
    long1-user longitude
    lat2-branch latitude
    long2-branch longitude
    """
    R = 6371  # Yer radiusi (km)
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)

    a = (
        math.sin(dLat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dLon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def nearest_branches_func(branch_data, user_lat, user_lon):
        branches = [
            {
                "id": branch["id"],
                "name": branch["name"],
                "phone_number": str(branch["phone_number"]),
                "latitude": branch["latitude"],
                "longitude": branch["longitude"],
                "distance": round(
                    get_distance_from_lat_lon_in_km(
                        user_lat, user_lon, branch["latitude"], branch["longitude"]
                    ),
                    2,
                ),
            }
            for branch in branch_data
        ]

        # Masofaga qarab saralash va 5 ta eng yaqinini olish
        nearest = sorted(branches, key=lambda x: x["distance"])[:5]
        return nearest


def normalize_phone(phone):
    """Telefon raqamdan bo'sh joy, + va - belgilarini olib tashlab, faqat raqamlarni qaytaradi"""
    digits = "".join(filter(str.isdigit, phone))
    if digits.startswith("998") and len(digits) == 12:
        return "+" + digits
    elif digits.startswith("0") and len(digits) == 9:
        return "+998" + digits[1:]
    elif len(digits) == 9:
        return "+998" + digits
    elif digits.startswith("+") and len(digits) == 13:
        return digits
    return "+" + digits
