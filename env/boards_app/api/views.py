from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.db.models import Count, Q
from boards_app.models import Board
from .serializers import BoardSerializer
from .permissions import IsBoardMember

class BoardList(generics.ListCreateAPIView):
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return (Board.objects
                .filter(Q(owner = user) | Q(members = user))
                .annotate(
                    member_count = Count("members", distinct=True),
                    ticket_count = Count("tasks", distinct=True),
                    tasks_to_do_count = Count("tasks", filter = Q(tasks__status="to-do"), distinct=True),
                    tasks_high_prio_count = Count("tasks", filter = Q(tasks__priority="high"), distinct=True)
                ).distinct()
            )
        
    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx
    
class BoardDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsBoardMember]