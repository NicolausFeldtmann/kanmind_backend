from django.db import models
from django.contrib.auth.models import User

# Class to define UserEmail including User, Username and associated email address
class UserEmail(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=30)
    usermail = models.EmailField(max_length=50)
    
    def __str__(self):
        return self.usermail