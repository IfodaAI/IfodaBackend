from rest_framework.permissions import BasePermission


class PostAndCheckUserOnly(BasePermission):
    """
    ADMIN -> hamma narsaga full access
    Oddiy user ->
        - PATCH faqat autentifikatsiya bilan (o'zining obyektini)
        - GET faqat check_user action ruxsat
        - Qolganlari taqiqlanadi
    """

    def has_permission(self, request, view):
        user = request.user

        # ADMIN yoki superuser uchun full ruxsat
        if user.is_authenticated and (user.role == "ADMIN" or user.is_superuser):
            return True

        # check_user action — GET ruxsat (anonim ham)
        if getattr(view, "action", None) == "check_user":
            return request.method == "GET"

        # PATCH faqat autentifikatsiya bilan
        if request.method == "PATCH":
            return user.is_authenticated

        return False

    def has_object_permission(self, request, view, obj):
        user = request.user

        # ADMIN yoki superuser — full access
        if user.role == "ADMIN" or user.is_superuser:
            return True

        # PATCH — faqat o'zining obyektini
        if request.method == "PATCH":
            # TelegramUser uchun: user fieldi orqali tekshirish
            if hasattr(obj, "user_id"):
                return obj.user_id == user.id
            # User uchun: to'g'ridan-to'g'ri ID tekshirish
            return obj.id == user.id

        return True