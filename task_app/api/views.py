from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied, NotFound
from django.db.models import Count
from task_app.models import Task, Comment
from boards_app.models import Board
from .serializers import TaskSerializer, CommentSerializer
from .permissions import IsBoardMember

class TaskListView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsBoardMember]
    
    def get_queryset(self):
        user = self.request.user
        board_id = self.request.query_params.get("board")
        qs = (
            Task.objects.all()
            .select_related("assignee", "reviewer", "board")
            .annotate(comments_count=Count("comments", distinct=True))
        )
        if board_id:
            try:
                board = Board.objects.get(pk=board_id)
            except Board.DoesNotExist:
                return Task.objects.none()
            if not board.members.filter(pk=user.pk).exists() and board.owner_id != user.pk and not (user.is_staff or user.is_superuser):
                raise PermissionDenied("Acces denied")
            return qs.filter(board_id=board_id)
        return qs.filter(board__members=user) | qs.filter(board__owner=user)
        
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data =request.data)
        serializer.is_valid(raise_exception = True)
        board_id = request.data.get("board")
        if board_id is None: return Response({"error": "Invalid request data"}, status=status.HTTP_400_BAD_REQUEST)
        try:board = Board.objects.get(pk = board_id)
        except Board.DoesNotExist:
            return Response({"error": "Board not found"}, status=status.HTTP_404_NOT_FOUND)
        if not board.members.filter(pk = request.user.pk).exists():
            return Response({"error": "Access denied."}, status=status.HTTP_403_FORBIDDEN)
        try: self.perform_create(serializer, board =board)
        except Exception:
            return Response({"error": "Intern server problem"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers = headers)
    
    def perform_create(self, serializer, board = None):
        serializer.save(board = board)
        
class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsBoardMember]
    
    def get_queryset(self):
        return (
            Task.objects.all()
            .select_related("assignee", "reviewer", "board")
            .annotate(comments_count = Count("comments", distinct=True))
        )
        
class AssignedToMeList(generics.ListAPIView):
    serializer_class = TaskSerializer
    
    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Task.objects.none()
        return (
            Task.objects.filter(assignee = user)
            .select_related("assignee", "reviewer", "board")
            .annotate(comments_count = Count("comments", distinct=True))
        )
        
class TaskReviewerList(generics.ListAPIView):
    serializer_class = TaskSerializer
    
    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Task.objects.none()
        return(
            Task.objects.filter(reviewer = user)
            .select_related("assignee", "reviewer", "board")
            .annotate(comments_count = Count("comments", distinct=True))
        )
        
class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsBoardMember]
    
    def get_queryset(self):
        task_id = self.kwargs["task_id"]
        try:
            task = Task.objects.select_related("board").get(pk=task_id)
        except Task.DoesNotExist:
            raise NotFound("Task not found")
        board = task.board
        user = self.request.user
        if not (user.is_superuser or user.is_staff or board.owner_id == user.id or board.members.filter(pk=user.pk).exists()):
            raise PermissionDenied("Access deneid")
        return Comment.objects.filter(task_id=task_id).order_by("created_at")
    
    def create(self, request, *args, **kwargs):
        if not isinstance(request.data, dict):
            return Response({"error": "Invalid request."}, status=status.HTTP_400_BAD_REQUEST)
        
        content = request.data.get("content")
        if content is None:
            return Response({"error": "Content is required"}, status=status.HTTP_400_BAD_REQUEST)
        if not isinstance(content, str) or not content.strip():
            return Response({"error": "Content is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            self.perform_create(serializer)
        except PermissionDenied:
            return Response({"error": "Access denied"}, status=status.HTTP_403_FORBIDDEN)
        except NotFound:
            return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return Response({"error": "Internal server problem"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def perform_create(self, serializer):
        task_id = self.kwargs["task_id"]
        try:
            task = Task.objects.get(pk=task_id)
        except Task.DoesNotExist:
            raise NotFound("Task not found")
        serializer.save(task=task)
        
class CommentDeleteView(generics.DestroyAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsBoardMember]
    lookup_url_kwarg = "comment_id"
    
    def get_queryset(self):
        task_id = self.kwargs["task_id"]
        return Comment.objects.filter(task_id = task_id)