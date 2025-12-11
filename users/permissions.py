from rest_framework.permissions import BasePermission

class PostAndCheckUserOnly(BasePermission):
    """
    ADMIN -> hamma narsaga full access
    Oddiy user ->
        - POST va PATCH ruxsat
        - GET faqat check_user action ruxsat
        - Qolganlari taqiqlanadi
    """

    def has_permission(self, request, view):
        user = request.user

        # 1️⃣ ADMIN yoki superuser uchun full ruxsat
        if user.is_authenticated and (user.role == "ADMIN" or user.is_superuser):
            return True

        # 2️⃣ check_user action — faqat GET ruxsat
        if getattr(view, "action", None) == "check_user":
            return request.method == "GET"

        # 3️⃣ POST va PATCH ruxsat
        if request.method in ["POST", "PATCH"]:
            return True

        # 4️⃣ Qolgan hamma deny
        return False