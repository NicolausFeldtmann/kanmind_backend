from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from task_app.models import Task, Comment
from django.db.models import Count
from .serializers import TaskSerializer, CommentSerializer
from .permissions import IsStaffOrReadOnly, IsAdminForDeleteOrPatchAndReadOnly, IsOwnerOrAdmin

class TaskListView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return (
            Task.objects.all()
            .select_related("assignee", "reviewer", "board")
            .annotate(comments_count = Count("comments", distinct=True))
        )
        
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
        return(
            Task.objects.filter(assignee = user)
            .select_related("assignee", "reviewer", "board")
            .annotate(comments_count=Count("comments", distinct=True))
        )
    
class TaskReviewList(generics.ListAPIView):
    serializer_class = TaskSerializer
    
    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Task.objects.none()
        return (
            Task.objects.filter(reviewer = user)
            .select_related("assignee", "reviewer", "board")
            .annotate(comments_count = Count("comments", distinct=True))
        )
        
class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        task_id = self.kwargs["task_id"]
        return Comment.objects.filter(task_id=task_id).order_by("created_at")
    
    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx
    
    def perform_create(self, serializer):
        task_id = self.kwargs["task_id"]
        serializer.save(task_id=task_id)
        
class CommentDeleteView(generics.DestroyAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = "comment_id"
    
    def get_queryset(self):
        task_id = self.kwargs["task_id"]
        return Comment.objects.filter(task_id=task_id)