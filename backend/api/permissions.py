from rest_framework import permissions


class ReadOnlyPermission(permissions.BasePermission):
    """Read Only permission."""

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class DenyAll(permissions.BasePermission):
    """Permission to block unused Djoser endpoints."""

    def has_permission(self, request, view):
        return False


class IsAuthorOfContentOrReadOnly(permissions.BasePermission):
    """Content editing allowed only to the author of content."""
    msg = 'Изменение чужого контента запрещено!'

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user == obj.author
