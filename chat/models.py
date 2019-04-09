from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.

class Room(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Message(models.Model):
    author = models.ForeignKey(User, related_name='author_messages', on_delete=models.CASCADE, blank=True, null=True)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    is_bot = models.BooleanField(null=True, default=False)
    read = models.BooleanField(null=True, default=False)

    def __str__(self):
        return self.author.username if self.author else 'BOT'

    def last_50_messages(self, room):
        return Message.objects.order_by('timestamp').all()[:50]



