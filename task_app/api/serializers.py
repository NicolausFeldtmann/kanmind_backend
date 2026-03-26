from rest_framework import serializers
from django.contrib.auth.models import User
from task_app.models import Task, Comment

""" Serializer konvert incommig data to fullname """
class UserFullnameSerializer(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ["id", "email", "fullname"]
        
    def get_fullname(self, obj):
        return obj.get_full_name() or obj.username
    
""" Convert incomming data relevant for comment. Containing id, commentauthor, comment and timestamp of post. """
class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField(read_only = True)
    
    class Meta:
        model = Comment
        fields = ["id", "author", "content", "created_at"]
    """ Get author fullname or username """    
    def get_author(self, obj):
        return obj.author.get_full_name() or obj.author.username
    
    """ Creats comment. return commentauthor and validated data """
    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user if request else None
        return Comment.objects.create(author = user, **validated_data)
    
""" Main serializer. Containig multiple fields like userrole, id, title, descriptions, etc. """
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
    
    comments_count = serializers.SerializerMethodField(read_only = True)
    
    class Meta:
        model = Task
        fields = [
            "id",
            "board",
            "title",
            "description",
            "status",
            "priority",
            "assignee",
            "reviewer",
            "assignee_id",
            "reviewer_id",
            "due_date",
            "comments_count"
        ]
        
    def get_comments_count(self, obj):
        return getattr(obj, "comments_count", None) or obj.comments.count()