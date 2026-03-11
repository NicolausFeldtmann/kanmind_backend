from django.db import models
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from boards_app.models import Board
from .serializers import BoardSerializer
from .permissions import IsBoardMember

# View suports GET and POST request for board list.
class BoardList(generics.ListCreateAPIView):
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return Board.objects.filter(members = user) | Board.objects.filter(owner = user)
    
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

# View suports GET, POST/UPDATE and DELETE request for single board.
class BoardDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated, IsBoardMember]
    
    def get_object_or_404(self):
        try:
            return Board.objects.get(pk = self.kwargs.get(self.lookup_field or "pk"))
        except Board.DoesNotExist:
            raise NotFound()
        
    def retrieve(self, request, *args, **kwargs):
        try:
            obj = self.get_object_or_404()
            self.check_object_permissions(request, obj)
        except PermissionDenied:
            return Response({"error": "Access denied"}, status=status.HTTP_403_FORBIDDEN)
        except NotFound:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(obj)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def update(self, request, *args, **kwargs):
        try:
            obj = self.get_object_or_404()
            self.check_object_permissions(request, obj)
        except PermissionDenied:
            return Response({"error": "Access denied"}, status=status.HTTP_403_FORBIDDEN)
        except NotFound:
            return Response({"error": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(obj, data = request.data, partial=kwargs.get("partial", False))
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        try:
            obj = self.get_object_or_404()
            self.check_object_permissions(request, obj)
        except PermissionDenied:
            return Response({"error": "Access denied"}, status=status.HTTP_403_FORBIDDEN)
        except NotFound:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        
        self.perform_destroy(obj)
        return Response(status=status.HTTP_204_NO_CONTENT)