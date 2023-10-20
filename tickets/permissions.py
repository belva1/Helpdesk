from rest_framework import permissions


class HelpdeskPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if view.action == 'destroy':
            return request.user.is_staff

        if view.action == 'partial_update':

            if request.user.is_staff:
                return False

            if request.user == obj.ticket_user:
                allowed_fields = ['priority', 'description']
                update_fields = request.data.keys()
                for field in update_fields:
                    if field not in allowed_fields:
                        return False
                return True

        return request.user.is_staff or request.user == obj.ticket_user
