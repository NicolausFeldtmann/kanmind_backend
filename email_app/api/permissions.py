from rest_framework.permissions import BasePermission, SAFE_METHODS

""" Custom permission class. Allows DELETE request only admin or user of owner. """
class IsAdminForDeleteOrPatchAndReadOnly(BasePermission):
    
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        elif request.method == "DELETE":
            return bool(request.user and request.user.is_superuser)
        else:
            return bool(request.user and request.user.is_staff)