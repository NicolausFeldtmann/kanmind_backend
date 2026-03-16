from rest_framework import serializers
from boards_app.models import Board
from django.contrib.auth.models import User
from task_app.api.serializers import TaskSerializer
from email_app.api.serializers import UserEmailSerializer

class SimpleUserSerializer(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ["id", "email", "fullname"]
        
    def get_fullname(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()

class BoardUserSerializer(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ["id", "email", "fullname"]

class BoardSerializer(serializers.ModelSerializer):
    owner_data = SimpleUserSerializer(source="owner", read_only=True)
    members_data = SimpleUserSerializer(source="members", many=True, read_only=True)

    
    class Meta:
        model = Board
        fields = [
            "id",
            "title",
            "owner_data",
            "members_data",
        ]
        
    def create(self, validated_data):
        members = validated_data.pop("members", [])
        request = self.context.get("request")
        owner = request.user if request else None
        board = Board.objects.create(owner = owner, **validated_data)
        
        if members:
            board.members.set(members)
            
        if owner and not board.members.filter(pk = owner.pk).exists():
            board.members.add(owner)
        
        return board
    
    def update(self, instance, validated_data):
        members = validated_data.pop("members", None)
        for attr,value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if members is not None:
            instance.members.set(members)
        return instance
    
    