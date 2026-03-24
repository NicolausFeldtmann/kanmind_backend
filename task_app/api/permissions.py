from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.exceptions import NotFound
from boards_app.models import Board
from task_app.models import Task

class IsStaffOrReadOnly(BasePermission):
    
    def has_permission(self, request, view):
        is_staff = bool(request.user and request.user.is_staff)
        return is_staff or request.method in SAFE_METHODS
    
class IsAdminForDeleteOrPatchAndReadOnly(BasePermission):
    
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        elif request.method == "DELETE":
            return bool(request.user and request.user.is_superuser)
        else:
            return bool(request.user and request.user.is_staff)
        
class IsOwnerOrAdmin(BasePermission):
    
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        elif request.method == "DELETE":
            return bool(request.user and request.user.is_superuser)
        else:
            return bool(request.user and request.user == obj.user)
        
class IsBoardMember(BasePermission):
    
    def is_member_of_board(self, user, board_id):
        if not user or not user.is_authenticated:
            return False
        try:
            board = Board.objects.get(pk = board_id)
        except Board.DoesNotExist:
            raise NotFound("Board not found")
        if user.is_superuser or user.is_staff:
            return True
        if board.owner_id == user.id:
            return True
        return board.members.filter(pk=user.pk).exists()
    
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            board_id = request.query_params.get("board") or request.data.get("board")
            if board_id:
                return self.is_member_of_board(request.user, board_id)
            return True
        
        if request.method == "POST":
            board_id = request.data.get("board")
            if board_id:
                return self.is_member_of_board(request.user, board_id)
            return False
        return bool(request.user and request.user.is_authenticated)
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser or user.is_staff:
            return True
        
        board = None
        if hasattr(obj, "board"):
            board = obj.board
        elif hasattr(obj, "task") and hasattr(obj.task, "board"):
            board = obj.task.board
        elif hasattr(obj, "owner_id") or hasattr(obj, "members"):
            board = obj
        if not board:
            return False
        if board.owner_id == user.id:
            return True
        return board.members.filter(pk=user.pk).exists()