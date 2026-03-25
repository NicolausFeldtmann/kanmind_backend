from rest_framework import serializers
from boards_app.models import Board
from django.contrib.auth.models import User
from task_app.api.serializers import TaskSerializer

class BoardUserSerializer(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ["id", "email", "fullname"]
        
    def get_fullname(self, obj):
        return obj.get_full_name() or obj.username

class BoardSerializer(serializers.ModelSerializer):
    owner_id = serializers.IntegerField(source="owner.id", read_only = True)
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Board
        fields = [
            "id",
            "title",
            "member_count",
            "ticket_count",
            "tasks_to_do_count",
            "tasks_high_prio_count",
            "owner_id",
        ]
        read_only_fields = [
            "owner_id",
            "member_count",
            "ticket_count",
            "tasks_to_do_count",
            "tasks_high_prio_count"
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
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if members is not None:
            instance.members.set(members)
        return instance
    
    def get_member_count(self, obj):
        return  obj.members.count()
    
    def get_ticket_count(self, obj):
        return obj.tasks.count()
    
    def get_tasks_to_do_count(self, obj):
        return obj.tasks.filter(status="to-do").count() 
    
    def get_tasks_high_prio_count(self, obj):
        return obj.tasks.filter(priority="high").count() 
    
class BoardDetailSerializer(BoardSerializer):
    owner_id = serializers.IntegerField(source="owner.id", read_only=True)
    members = BoardUserSerializer(many=True, read_only=True)
    tasks = TaskSerializer(many=True, read_only=True)
    
    class Meta:
        model = Board
        fields = [
            "id",
            "title",
            "owner_id",
            "members",
            "tasks",
        ]
        
class BoardOwnerSerializer(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ["id", "email", "fullname"]
        
    def get_fullname(self, obj):
        return obj.get_full_name() or obj.username
    
class BoardPatchSerializer(serializers.ModelSerializer):
    owner_data = BoardOwnerSerializer(source="owner", read_only=True)
    members_data = BoardOwnerSerializer(source="members", many=True, read_only=True)
    
    class Meta:
        model = Board
        fields = ["id", "title", "owner_data", "members_data"]