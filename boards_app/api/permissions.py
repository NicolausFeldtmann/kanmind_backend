from rest_framework.permissions import BasePermission,  SAFE_METHODS
        
""" Custom permission class. Differentiated acces of user and boardmembers """
class IsBoardMember(BasePermission):
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser or user.is_staff:
            return True
        if getattr(obj, "owner_id", None) == user.id:
            return True
        return obj.members.filter(pk=user.pk).exists()