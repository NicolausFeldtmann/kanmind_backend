from task_app.models import Task
from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.exceptions import NotFound
from boards_app.models import Board
        
""" Custom permission class. Checks if user is board member or owner. """
""" Get board in relation to task. """
class IsBoardMember(BasePermission):
    
    """ Function detects if user is board member or owner """
    def is_member_of_board(self, user, board_id):
        if not user or not user.is_authenticated:
            return False
        try:
            board = Board.objects.get(pk=board_id)
        except Board.DoesNotExist:
            raise NotFound("Board not found")
        if user.is_superuser or user.is_staff:
            return True
        if board.owner_id == user.id:
            return True
        return board.members.filter(pk=user.pk).exists()
    
    """ Get tasks ids """
    def get_task_id(self, view):
        kwargs = getattr(view, "kwargs", {}) or {}
        for key in ("task_id", "taskId", "pk", "id"):
            if key in kwargs and kwargs[key]:
                try:
                    return int(kwargs[key])
                except Exception:
                    pass
        
        for v in kwargs.values():
            try:
                return int(v)
            except Exception:
                continue
        return None
    
    """ Function to get board ids. """
    def get_board_id(self, request):
        return request.query_params.get("board") or request.data.get("board")
    
    """ Defines permission for authenticated users. Returns statuscode 404 if Task didn't exists. """
    def has_permission(self, request, view):
        task_id = self.get_task_id(view)
        if task_id:
            try:
                task = Task.objects.select_related("board").get(pk=task_id)
            except Task.DoesNotExist:
                raise NotFound("Task bot found")
            return self.is_member_of_board(request.user, task.board_id)
        
        if request.method in SAFE_METHODS:
            board_id = self.get_board_id(request)
            if board_id:
                return self.is_member_of_board(request.user, board_id)
            return True
        
        if request.method == "POST":
            board_id = request.data.get("board")
            if board_id:
                return self.is_member_of_board(request.user, board_id)
            return False
        
        return bool(request.user and request.is_authenticated)
    
    """ Defines permissions for staff, admin, and owner. """
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