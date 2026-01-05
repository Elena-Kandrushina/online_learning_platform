from rest_framework import permissions


class IsModerator(permissions.BasePermission):
    """Разрешение для модераторов"""

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.user.groups.filter(name='moderators').exists()
        return False


class IsOwnerOrModerator(permissions.BasePermission):
    """Разрешение для владельца или модератора"""

    def has_object_permission(self, request, view, obj):

        if hasattr(obj, 'owner'):
            is_owner = obj.owner == request.user
        elif hasattr(obj, 'author'):
            is_owner = obj.author == request.user
        else:
            is_owner = False


        is_moderator = request.user.groups.filter(name='moderators').exists()

        return is_owner or is_moderator


class IsNotModerator(permissions.BasePermission):
    """Разрешение для НЕ модераторов (только для создания/удаления)"""

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return not request.user.groups.filter(name='moderators').exists()
        return False
