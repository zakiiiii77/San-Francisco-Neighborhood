from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Room(models.Model):
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(User, related_name='rooms', through='RoomMember')

    def __str__(self):
        return self.name

class Task(models.Model):
    room = models.ForeignKey(
        Room, 
        on_delete=models.CASCADE,
        related_name='tasks'
    )
    description = models.CharField(max_length=255)
    completed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tasks')
    is_completed = models.BooleanField(default=False)

class Comment(models.Model):
    task = models.ForeignKey(
        Task, 
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)    
    created_at = models.DateTimeField(auto_now_add=True)

class RoomMember(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)
