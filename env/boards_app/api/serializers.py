from rest_framework import serializers
from boards_app.models import Board
from django.contrib.auth.models import User
from task_app.api.serializers import TaskSerializer

class UserShortSerializer(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ["id", "email", "username", "fullname"]
        
    def get_fullname(self, obj):
        return obj.get_full_name() or obj.username
    
class BoardSerializer(serializers.ModelSerializer):
    members = UserShortSerializer(many=True, read_only=True)
    member_ids = serializers.PrimaryKeyRelatedField(
        source = "members",
        queryset = User.objects.all(),
        many = True,
        required = False  
    )
    
    member_count = serializers.IntegerField(read_only = True)
    ticket_count = serializers.IntegerField(read_only = True)
    tasks_to_do_count = serializers.IntegerField(read_only = True)
    tasks_high_prio_count = serializers.IntegerField(read_only = True)
    tasks = TaskSerializer(many = True, read_only = True)
    
    class Meta:
        model = Board
        fields = [
            "id", "title", "owner", "members", "member_ids", "tasks", "member_count",
            "ticket_count", "tasks_to_do_count", "tasks_high_prio_count"
        ]
        read_only_fields = ["owner"]
        
    def to_internal_value(self, data):
        data = data.copy()
        if "members" in data and "member_ids" not in data:
            try:
                members_value = data.getlist("members")
            except ArithmeticError:
                members_value = data["members"]
                
            data["member_ids"] = members_value
            
        return super().to_internal_value(data)
    
    def update(self, instance, validated_data):
        members = validated_data.pop("members", None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if members is not None:
            instance.members-set(members)
        return instance