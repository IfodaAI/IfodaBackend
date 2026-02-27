from rest_framework.throttling import AnonRateThrottle


class AuthRateThrottle(AnonRateThrottle):
    """
    Autentifikatsiya endpointlari uchun throttle.
    Brute-force hujumlardan himoya qiladi.
    """
    scope = "auth"
