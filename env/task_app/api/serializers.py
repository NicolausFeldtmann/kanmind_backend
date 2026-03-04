from rest_framework import serializers
from django.contrib.auth.models import User
from task_app.models import Task, Comment
from django.db.models import Count

# Serializer for definig addable User
class UserFullnameSerializer(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ["id", "email", "fullname"]
        
    # Get Fullname or stored username
    def get_fullname(self, obj):
        return obj.get_full_name() or obj.username
    
# Serializer for definig comments
class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Comment
        fields = ["id", "author", "content", "created_at"]
        
    # Get fullname or stored username as comment author.
    def get_author(self, obj):
        return obj.author.get_full_name() or obj.author.username
    
    # Creats comment
    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user if request else None
        return Comment.objects.create(author=user, **validated_data)
    
# Serializer for defining tasks
class TaskSerializer(serializers.ModelSerializer):
    assignee = UserFullnameSerializer(read_only = True)
    reviewer = UserFullnameSerializer(read_only = True)
    
    assignee_id = serializers.PrimaryKeyRelatedField(
        source = "assignee",
        queryset = User.objects.all(),
        write_only = True,
        required = False,
        allow_null = True
    )
    
    reviewer_id = serializers.PrimaryKeyRelatedField(
        source = "reviewer",
        queryset = User.objects.all(),
        write_only = True,
        required = False,
        allow_null = True
    )
    
    comments_count = serializers.IntegerField(read_only = True)
    
    class Meta:
        model = Task
        fields = [
            "id",
            "board",
            "title",
            "description",
            "status",
            "priority",
            "due_date",
            "assignee",
            "reviewer",
            "assignee_id",
            "reviewer_id",
            "comments_count"
        ]