from rest_framework import permissions


class AuthorAdminPermission(permissions.BasePermission):
    """
    Неавторизированным пользователям разрешён только просмотр.
    Администратору или владельцу записи доступны остальные методы.
    """
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user
                or request.user.is_superuser)


class AdminOrReadOnlyPermission(permissions.BasePermission):
    """
    Неавторизированным пользователям разрешён только просмотр.
    Администратору доступны остальные методы.
    """
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_admin)
