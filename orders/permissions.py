# api/permissions.py (DRF permissions)
from rest_framework.permissions import BasePermission, SAFE_METHODS


class OrderPermission(BasePermission):
    """
    Rules:
    - Admin: all access
    - Manager: can read/update orders only if order.branch == manager.branch
    - Dispatcher: can read all orders (read-only)
    - User: can read their own orders (read-only)
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Admin full access
        if request.user.is_superuser or request.user.role == "ADMIN":
            return True

        # POST (create) allowed for regular users (they create their own orders)
        if request.method == "POST":
            return True

        # For non-object-level methods, allow access; object-level will restrict further
        # But block write operations for dispatchers and regular users
        if request.method not in SAFE_METHODS:
            return request.user.role in ("ADMIN", "MANAGER")

        return True

    def has_object_permission(self, request, view, obj):
        # Admin full access
        if request.user.is_superuser or request.user.role == "ADMIN":
            return True

        # Manager: can view & modify only orders of their branch
        if request.user.role == "MANAGER":
            # ensure manager has branch assigned
            if obj.branch_id is None or request.user.branch_id is None:
                return False
            return obj.branch_id == request.user.branch_id

        # Dispatcher: can read all orders, cannot modify
        if request.user.role == "DISPATCHER":
            return request.method in SAFE_METHODS

        # Regular user: read-only for own orders
        if request.user.role == "USER":
            return request.method in SAFE_METHODS and obj.user_id == request.user.id

        return False
