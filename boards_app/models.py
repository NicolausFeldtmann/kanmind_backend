from django.db import models
from django.contrib.auth.models import User

""" Class to define board members and containing components. """
class BoardMember(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    board = models.ForeignKey('boards_app.Board', on_delete=models.CASCADE, default="")
    name = models.CharField(max_length=30)
    email = models.EmailField(max_length=50, blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username} ({self.board.title})"
    
""" Class to define boards and containing components like boardowner and added users. """
class Board(models.Model):
    title = models.CharField(max_length=30)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owned_boards")
    members = models.ManyToManyField(User, related_name="boards", blank=True)
    
    def __str__(self):
        return self.title