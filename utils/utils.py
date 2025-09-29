import math

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

    a = (math.sin(dLat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dLon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c