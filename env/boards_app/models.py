from django.db import models
from django.contrib.auth.models import User

# Class to define a board member
class BoardMember(models.Model):
    name = models.CharField(max_length=30)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    email = models.EmailField(max_length=50, blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username} ({self.board.title})"
    
# Class to define a board
class Board(models.Model):
    title = models.CharField(max_length=30)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owned_boards")
    members = models.ManyToManyField(User, related_name="boards", blank=True)
    
    def __str__(self):
        return self.title