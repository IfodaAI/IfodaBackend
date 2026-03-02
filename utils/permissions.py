from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):
    """
    GET, HEAD, OPTIONS — hamma uchun ruxsat (anonim ham).
    POST, PUT, PATCH, DELETE — faqat ADMIN yoki superuser.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return (
            request.user.is_authenticated
            and (request.user.is_superuser or getattr(request.user, "role", None) == "ADMIN")
        )
