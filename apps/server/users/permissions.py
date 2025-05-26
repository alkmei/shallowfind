from rest_framework.permissions import BasePermission


class IsAdminOrSelf(BasePermission):
    """
    - list & create: admin only
    - retrieve/update/partial_update: admin or the user themselves
    """

    def has_permission(self, request, view):
        if view.action in ["list", "create"]:
            return bool(request.user and request.user.is_staff)
        # Other actions require authentication
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        # Safe methods (GET, HEAD, OPTIONS) and write (PUT, PATCH) on detail:
        # allow if admin or the object belongs to the requesting user
        return bool(request.user.is_staff or obj == request.user)
