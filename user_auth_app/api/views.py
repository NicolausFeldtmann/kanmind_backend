from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from user_auth_app.models import UserProfile
from .serializers import UserProfileSerializer, RegistrationSerializer, EmailAuthSerializer

# View suports GET, POST/UPDATE, DESTROY request for single userprofile. 
class UserProfileDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    
# View suports GET and POST request to registrate userprofile
class RegistrationView(APIView):
    permission_classes = [AllowAny]
    
    # Post request that returns created informations or bad request status.
    def post(self, request):
        serializer = RegistrationSerializer(data = request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user = user)
            fullname = f"{user.first_name} {user.last_name}".strip()
            data = {
                "token": token.key,
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
                "fullname": fullname
            }
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# View suports POST request to log in.
class CustomLoginView(ObtainAuthToken):
    permission_classes = [AllowAny]
    serializer_class = EmailAuthSerializer
    
    # Post request that returns infromations containing Authtoken, if login attempt is valid.
    def post(self, request):
        serializer = self.serializer_class(data = request.data)
        
        data ={}
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            token, create = Token.objects.get_or_create(user = user)
            fullname = f"{user.first_name} {user.last_name}"
            data = {"token": token.key, "user_id": user.id, "username": user.username, "email": user.email, "fullname": fullname}
        else:
            return Response({"error": "Wrong emai or password"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(data)
    
# View suports GEr requests
class CheckEmailView(APIView):
    permission_classes = [IsAuthenticated]
    
    # Get request returns name, email, id if email exists. Returns error else.
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