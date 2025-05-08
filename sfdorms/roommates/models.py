from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Room(models.Model):
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(User, related_name='rooms', through='RoomMember')

    def __str__(self):
        return self.name
    
class TodoItem(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='todos')
    text = models.CharField(max_length=255)
    is_done = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text
    
class Comment(models.Model):
    todo = models.ForeignKey(TodoItem, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} on {self.todo.text}"

class RoomMember(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)

class Task(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    completed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='completed_tasks')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tasks', null=True)
    is_completed = models.BooleanField(default=False)