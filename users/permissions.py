from rest_framework.permissions import BasePermission

class PostAndCheckUserOnly(BasePermission):
    """
    Faqat:
      - POST (create) ruxsat
      - check_user (GET action) ruxsat
      Qolganlariga taqiq
    """

    def has_permission(self, request, view):
        # check_user action faqat GET da ruxsat
        if hasattr(view, "action") and view.action == "check_user":
            return request.method == "GET"

        # Faqat POST ga ruxsat
        if request.method in ["POST", "PATCH"]:
            return True

        # Qolgan hamma deny
        return False
