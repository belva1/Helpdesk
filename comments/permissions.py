from rest_framework import permissions


class HelpdeskPermissions(permissions.BasePermission):
    def has_permission(self, request, view):  # permission to the view access
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):  # permission to the object access
        # action from the view for the object
        if view.action == 'create':
            allowed_fields = ['text']
            create_fields = request.data.keys()
            for field in create_fields:
                if field not in allowed_fields:
                    return False
            return obj.ticket.status == 'InProcess'

        if view.action == 'destroy' or view.action == 'update' or view.action == 'partial_update':
            return request.user == obj.comment_user and obj.ticket.status == 'InProcess'

        return True
