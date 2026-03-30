from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count
from task_app.models import Task, Comment
from boards_app.models import Board
from .serializers import TaskSerializer, CommentSerializer
from .permissions import IsBoardMember

""" View for tasklist. Depending if user is boardmember. """
class TaskListView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsBoardMember]
    
    """ Get all tasks of a board, or all tasks user is boardmember or owner of. """
    def get_queryset(self):
        user = self.request.user
        qs = (
            Task.objects.all()
            .select_related("assignee", "reviewer", "board")
            .annotate(comments_count=Count("comments", distinct=True))
        )

        return qs.filter(board__members=user) | qs.filter(board__owner=user)
        
    """ POST task, if relatetd board exists and user is board member. Returns diferent statuscodes """
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data =request.data)
        serializer.is_valid(raise_exception = True)
        self.perform_create(serializer)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def perform_create(self, serializer, board = None):
        board_id =  self.request.data.get("board")
        board = Board.objects.get(pk=board_id)
        serializer.save(board=board)
  
""" View for single task. User musst be baord member. """      
class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsBoardMember]
    
    """ Get related fields and sum of comments. """
    def get_queryset(self):
        return (
            Task.objects.all()
            .select_related("assignee", "reviewer", "board")
            .annotate(comments_count = Count("comments", distinct=True))
        )
        
""" View for all tasks the user is assigned to. """
class AssignedToMeList(generics.ListAPIView):
    serializer_class = TaskSerializer
    
    """ Get related fields and sum of comments. """
    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Task.objects.none()
        return (
            Task.objects.filter(assignee = user)
            .select_related("assignee", "reviewer", "board")
            .annotate(comments_count = Count("comments", distinct=True))
        )
        
""" View for all tasks the user is assigned as reviewer. """        
class TaskReviewerList(generics.ListAPIView):
    serializer_class = TaskSerializer
    
    """ Get related fields and sum of comments. """
    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Task.objects.none()
        return(
            Task.objects.filter(reviewer = user)
            .select_related("assignee", "reviewer", "board")
            .annotate(comments_count = Count("comments", distinct=True))
        )

""" Lists all comments related to task. """        
class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsBoardMember]
    
    """ Gets comments if user is authenticated and related task exists. """
    def get_queryset(self):
        task_id = self.kwargs["task_id"]
        return Comment.objects.filter(task_id=task_id).order_by("created_at")
    
    """ POST comment. Validats content and handles several statuscodes. """
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def perform_create(self, serializer):
        task_id = self.kwargs["task_id"]
        task = Task.objects.get(pk=task_id)
        serializer.save(task=task)

""" View deletes comment. Uses custompermission class and athenticates only owner and admin. """        
class CommentDeleteView(generics.DestroyAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsBoardMember]
    lookup_url_kwarg = "comment_id"
    
    def get_queryset(self):
        task_id = self.kwargs["task_id"]
        return Comment.objects.filter(task_id = task_id)