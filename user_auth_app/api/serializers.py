from django.utils.text import slugify
from rest_framework import serializers
from user_auth_app.models import UserProfile
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from itertools import count

User = get_user_model()

# Defines User Profile and containing informations.
class UserProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField(read_only = True)
    
    class Meta:
        model = UserProfile
        fields = ["user", "email", "first_name", "last_name", "full_name"]
        
    # returns the full username.
    def get_full_name(self, obj):
        return obj.full_name()
   
# Definies all necessary informations to create an account.
class RegistrationSerializer(serializers.ModelSerializer):
    repeated_password = serializers.CharField(write_only = True)
    fullname = serializers.CharField(write_only = True)
    
    class Meta:
        model = User
        fields = ["fullname", "email", "password", "repeated_password"]
        extra_kwargs = {"password": {"write_only": True}}
        
    # Assures that email is not already taken
    def validate_email(self, value):
        if User.objects.filter(email__iexact = value).exists():
            raise serializers.ValidationError({"errpr": "Email already in use."})
        return value
    
    # Assurdes that password and repeated password match.
    def validate(self, data):
        if data.get("password") != data.get("repeated_password"):
            return serializers.ValidationError({"error": "Passwords don't match."})
        return data
    
    # Creates Userprofile containing previously validated infromations.
    def create(self, validated_data):
        fullname = validated_data.pop("fullname", "").strip()
        first_name, last_name = (fullname.split(None, 1) + [""])[:2]
        email = validated_data.pop("email")
        password = validated_data.pop("password")
        base = slugify(f"{first_name} {last_name}") or slugify(email.split("@", 1)[0])
        username = base
        for i in count(1):
            if not User.objects.filter(username = username).exists():
                break
            username = f"{base}{i}"
        user = User(first_name=first_name, last_name=last_name, email=email, username=username)
        user.set_password(password)
        user.save()
        UserProfile.objects.create(user=user, first_name=first_name, last_name=last_name, email=email)
        return user

# Assures that password and email are valid
class EmailAuthSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(style={"input_type": "password"}, trim_whitespace = False)
    
    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")
        
        try:
            user = User.objects.get(email__iexact = email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"error": "Invalid access"})
        
        if not user.check_password(password):
            raise serializers.ValidationError({"error": "Invalid access"})
        
        attrs["user"] = user
        return attrs