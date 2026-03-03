from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from .serializers import UserEmailSerializers

User = get_user_model()

class UserEmailViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserEmailSerializers
    
    def list(self, request, *args, **kwargs):
        email = request.query_params.get("email")
        if email:
            try:
                user = User.objects.get(email__iexact=email)
            except User.DoesNotExist:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
            serializer = self.get_serializer(user)
            return Response(serializer.data)
        
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)