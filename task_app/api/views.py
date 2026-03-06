from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from task_app.models import Task, Comment
from django.db.models import Count
from .serializers import TaskSerializer, CommentSerializer
from .permissions import IsStaffOrReadOnly, IsAdminForDeleteOrPatchAndReadOnly, IsOwnerOrAdmin

# View suports GET and POST request
class TaskListView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    
    # Delivers task Query
    def get_queryset(self):
        return (
            Task.objects.all()
            .select_related("assignee", "reviewer", "board")
            .annotate(comments_count = Count("comments", distinct=True))
        )
    
# View suports GET, POST/UPDATE, DELETE request for single tasks.    
class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    
    # Deliver task query
    def get_queryset(self):
        return (
            Task.objects.all()
            .select_related("assignee", "reviewer", "board")
            .annotate(comments_count = Count("comments", distinct=True))
        )
        
# View suports GET requestfor tasks, user is member of.
class AssignedToMeList(generics.ListAPIView):
    serializer_class = TaskSerializer
    
    # Deliver for user relevant querys
    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Task.objects.none()
        return(
            Task.objects.filter(assignee = user)
            .select_related("assignee", "reviewer", "board")
            .annotate(comments_count=Count("comments", distinct=True))
        )
    
# View suports GET requestfor tasks, user is member of.
class TaskReviewList(generics.ListAPIView):
    serializer_class = TaskSerializer
    
    # Deliver for user relevant querys
    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Task.objects.none()
        return (
            Task.objects.filter(reviewer = user)
            .select_related("assignee", "reviewer", "board")
            .annotate(comments_count = Count("comments", distinct=True))
        )
        
# View suports GET and POST requests for comments
class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    
    # Delivers for task relevant query
    def get_queryset(self):
        task_id = self.kwargs["task_id"]
        return Comment.objects.filter(task_id=task_id).order_by("created_at")
    
    # Extends the context to include the current request
    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx
    
    # Creates comment for relevant task
    def perform_create(self, serializer):
        task_id = self.kwargs["task_id"]
        serializer.save(task_id=task_id)
 
# View suports DELETE request for comments       
class CommentDeleteView(generics.DestroyAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = "comment_id"
    
    # Extends the context to include the current request
    def get_queryset(self):
        task_id = self.kwargs["task_id"]
        return Comment.objects.filter(task_id=task_id)