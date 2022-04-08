from rest_framework import permissions


class ReadOnlyPermission(permissions.BasePermission):
    """Read Only permission."""

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class DenyAll(permissions.BasePermission):
    """Permission to block unused Djoser endpoints."""

    def has_permission(self, request, view):
        return False
