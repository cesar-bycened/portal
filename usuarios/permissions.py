from rest_framework.permissions import BasePermission


class EsSuperAdministrador(BasePermission):
    message = "Este servicio está reservado para el superadministrador."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_superuser
        )