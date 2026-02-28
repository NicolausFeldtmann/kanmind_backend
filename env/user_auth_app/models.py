from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30,default="")
    last_name = models.CharField(max_length=30, default="")
    username = models.SlugField(blank=True, default="")
    email = models.EmailField(max_length=50)
    
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()