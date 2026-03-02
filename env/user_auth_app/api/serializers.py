from django.utils.text import slugify
from rest_framework import serializers
from user_auth_app.models import UserProfile
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

User = get_user_model()

class UserProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField(read_only = True)
    
    class Meta:
        model = UserProfile
        fields = ["user", "email", "first_name", "last_name", "full_name"]
        
    def get_full_name(self, obj):
        return obj.full_name()
    
class RegistrationSerializer(serializers.ModelSerializer):
    repeated_password = serializers.CharField(write_only = True)
    fullname = serializers.CharField(write_only = True)
    
    class Meta:
        model = User
        fields = ["fullname", "email", "password", "repeated_password"]
        extra_kwargs = {"password": {"write_only": True}}
        
    def validated_email(self, value):
        if User.objects.filter(email__iiexact = value).exists():
            raise serializers.ValidationError({"Email already in use."})
        return value
    
    def validate(self, data):
        if data.get("password") != data.get("repeated_password"):
            return serializers.ValidationError("Passwords don't match.")
        return data
    
    def create(self, validated_data):
        fullname = validated_data.pop("fullname", "").strip()
        parts = fullname.split()
        first_name = parts[0] if parts else ""
        last_name = " ".join(parts[1:]) if len(parts) > 1 else ""
        email = validated_data.pop("email")
        password = validated_data.pop("password")
        base_name = slugify(f"{first_name}  {last_name}") or slugify(email.split("@")[0])
        username = base_name
        counter = 1
        
        while User.objects.filter(username = username).exists():
            username = f"{base_name}{counter}"
            counter += 1
        
        user = User(
            first_name = first_name,
            last_name = last_name,
            email = email,
            username = username
        )
        user.set_password(password)
        user.save()
        
        UserProfile.objects.create(
            user = user,
            first_name = first_name,
            last_name = last_name,
            username = username,
            email = email
        )
        return user

class EmailAuthSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(style={"input_type": "password"}, trim_whitespace=False)
    
    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")
        
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return serializers.ValidationError("Invalid acces")
        
        if not user.check_password(password):
            raise serializers.ValidationError("invalid acces")
        
        attrs["user"] = user
        return attrs