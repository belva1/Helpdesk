from rest_framework import permissions


class HelpdeskPermissions(permissions.BasePermission):
    def has_permission(self, request, view):  # permission to the view access
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):  # permission to the object access
        # action from the view for the object
        if view.action == 'destroy' or view.action == 'update' or view.action == 'partial_update':
            return request.user == obj.ticket_user
        return request.user.is_staff or request.user == obj.ticket_user
