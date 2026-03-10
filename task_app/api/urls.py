from django.urls import path
from .views import TaskListView, TaskDetailView, AssignedToMeList, TaskReviewerList, \
    CommentListCreateView, CommentDeleteView
    
urlpatterns = [
    path('tasks/', TaskListView.as_view(), name='task-list'),
    path('tasks/<int:pk>/', TaskDetailView.as_view(), name='task-detail'),
    path('tasks/assigned-to-me/', AssignedToMeList.as_view(), name='tasks-assigned'),
    path('tasks/reviewing/', TaskReviewerList.as_view(), name='tasks-reviewing'),
    path('tasks/<int:task_id>/comments/', CommentListCreateView.as_view(), name='task-comments'),
    path('tasks/<int:task_id>/comments/<int:comment_id>/', CommentDeleteView.as_view(), name='task-comment-detail')
]
