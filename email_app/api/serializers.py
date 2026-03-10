from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

# Serializer for defining UserEmail
class UserEmailSerializer(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ["id", "username", "email", "fullname"]
        
    def get_fullname(self, obj):
        return obj.get_full_name() or obj.username