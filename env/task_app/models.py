from django.db import models
from django.contrib.auth.models import User
from boards_app.models import Board

# Defines tasks. Includes title, description, assignee, reviewer, creation date, priority, and status
class Task(models.Model):
    STATUS_CHOICES = [
        ("to-do", "To DO"),
        ("in-progress", "In Progress"),
        ("review", "Review"),
        ("done", "Done")
    ]
    
    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Meduim"),
        ("high", "Heigh"),
    ]
    
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=30)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="to-do")
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default="medium")
    assignee = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="assigned_tasks")
    reviewer = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="review_tasks")
    due_date = models.DateField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updateed_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

# Defines a comment. Includes associated task, author, time of post, and content.
class Comment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="task_comments")
    created_at = models.DateTimeField(auto_now_add=True)
    content = models.TextField(default="")
    
    def __str__(self):
        return f"{self.author.get_full_name() or self.author.username}: {self.content[:20]}"