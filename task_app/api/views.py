from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count
from task_app.models import Task, Comment
from boards_app.models import Board
from .serializers import TaskSerializer, CommentSerializer

class TaskListView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return (
            Task.objects.all()
            .select_related("assignee", "reviewer", "board")
            .annotate(comments_count = Count("comments", distinct=True))
        )
        
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
    permission_classes = [IsAuthenticated]
    
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
            Task.objects.filter(reviwer = user)
            .select_related("assignee", "reviewer", "board")
            .annotate(comments_count = Count("comments", distinct=True))
        )
        
class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        task_id = self.kwargs["task_id"]
        return Comment.objects.filter(task_id = task_id).order_by("created_at")
    
    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx
    
    def perform_create(self, serializer):
        task_id = self.kwargs["task_id"]
        serializer.save(task_id = task_id)
        
class CommentDeleteView(generics.DestroyAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = "comment_id"
    
    def get_queryset(self):
        task_id = self.kwargs["task_id"]
        return Comment.objects.filter(task_id = task_id)