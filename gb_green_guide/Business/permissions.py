# business/permissions.py
from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsOwnerOrReadOnly(BasePermission):
    """
    Read sab ke liye allowed. Write sirf owner ko allowed.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return getattr(obj, "owner_id", None) == getattr(request.user, "id", None)


class IsBusinessOwner(BasePermission):
    """
    Sirf role == 'business_owner' ko POST/create (ya jahan use karo) allow.
    """
    message = "Only business owners can perform this action."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "role", None) == "business_owner"
        )
