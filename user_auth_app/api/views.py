from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from user_auth_app.models import UserProfile
from .serializers import UserProfileSerializer, RegistrationSerializer, EmailAuthSerializer

""" View for single userprofile. """ 
class UserProfileDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    
""" View for sending POST request for userregistration. Unauthenticated users are allowed. """
class RegistrationView(APIView):
    permission_classes = [AllowAny]
    
    """ POST userdata if valid. Retruns token, fullname, email and id. Retruns statuscodes depending validation. """
    def post(self, request):
        serializer = RegistrationSerializer(data = request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user = user)
            fullname = f"{user.first_name} {user.last_name}".strip()
            data = {
                "token": token.key,
                "fullname": fullname,
                "email": user.email,
                "user_id": user.id,
            }
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
""" View for login. Allows unauthenticated users. """
class CustomLoginView(ObtainAuthToken):
    permission_classes = [AllowAny]
    serializer_class = EmailAuthSerializer
    
    """ POST if data from EmailAuthSerializer are valid. Gets or creats token. Return statuscods depending validation. """
    def post(self, request):
        serializer = self.serializer_class(data = request.data)
        
        data ={}
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            token, create = Token.objects.get_or_create(user = user)
            fullname = f"{user.first_name} {user.last_name}"
            data = {"token": token.key, "fullname": fullname, "email": user.email, "user_id": user.id}
        else:
            return Response({"error": "Wrong emai or password"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(data)
    
""" View returns userdata related to email. """
class CheckEmailView(APIView):
    permission_classes = [IsAuthenticated]
    
    """ Return userdata containing id, email and fullname, if given email exists in DB. """
    """ Returns statuscodes depending email exists or not. """
    def get(self, request):
        email = request.query_params.get("email")
        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return Response({"exists": "False"}, status=status.HTTP_404_NOT_FOUND)
        data = {
            "id": user.id,
            "email": user.email,
            "fullname": f"{user.first_name} {user.last_name}".strip()
        }
        return Response(data)