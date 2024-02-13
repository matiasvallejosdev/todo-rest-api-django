"""
Permissions personalized for users.
"""
from rest_framework import permissions


class UserIsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        print(request.user)
        return False
