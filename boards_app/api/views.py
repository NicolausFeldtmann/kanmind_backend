from django.db import models
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.permissions import IsAuthenticated
from boards_app.models import Board
from .serializers import BoardSerializer, BoardDetailSerializer, BoardPatchSerializer
from .permissions import IsBoardMember

""" View performs GET request for board list and POST request for a new board. User must be authenticated"""
class BoardList(generics.ListCreateAPIView):
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated]
    
    """ Filters all boards user is member or owner. Prefetch of tasks an members. """
    def get_queryset(self):
        user = self.request.user
        return Board.objects.filter(members = user) | Board.objects.filter(owner = user).prefetch_related('tasks', 'members')
    
    """ Posts validated data to create board. Catches validation and/or server errors. """
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            self.perform_create(serializer)
        except Exception:
            return Response({"error": "Intern serverproblem"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

""" View for single boards. User musst be owner or member. """
class BoardDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Board.objects.all().prefetch_related("tasks", "members")
    permission_classes = [IsAuthenticated, IsBoardMember]
    serializer_class = BoardSerializer
    
    """ Uses BoardDetailSerializer for GET requests, else BoardSerializer """
    def get_serializer_class(self):
        if self.request.method == "GET":
            return BoardDetailSerializer
        return BoardSerializer
    
    """ Update function. Detects if user is authoricated and data are valid. """
    def update(self, request, *args, **kwargs):
        partial = kwargs.get("partial", False)
        
        try:
            obj = self.get_object()
        except PermissionDenied:
            return Response({"error": "Acces denied"}, status=status.HTTP_403_FORBIDDEN)
        except NotFound:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(obj, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        response_serializer = BoardPatchSerializer(obj)
        return Response(response_serializer.data, status=status.HTTP_200_OK)