"""
Admin panel uchun umumiy mixin va yordamchi klasslar.
"""


class FullNameAdminMixin:
    """
    Admin panelda to'liq ismni ko'rsatish uchun mixin.
    Model `first_name` va `last_name` maydonlariga ega bo'lishi kerak.
    """

    def full_name(self, obj):
        first = getattr(obj, "first_name", "") or ""
        last = getattr(obj, "last_name", "") or ""
        return f"{first} {last}".strip() or "-"

    full_name.short_description = "To'liq ism"
