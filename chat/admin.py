from django.contrib import admin

# Register your models here.
from .models import Message, Room

admin.site.register(Message)
admin.site.register(Room)
