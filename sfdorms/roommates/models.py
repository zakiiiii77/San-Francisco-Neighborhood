from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Room(models.Model):
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(User, related_name='rooms')

    def __str__(self):
        return self.name
    
class TodoItem(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='todos')
    text = models.CharField(max_length=255)
    is_done = models.BooleanField(default=False)

    def _str_(self):
        return self.text
    