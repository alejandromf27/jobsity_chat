# chat/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.safestring import mark_safe
import json
from .models import Room, Message

def index(request):
    rooms = Room.objects.all()
    return render(request, 'chat/index.html', {'rooms': rooms})

@login_required
def room(request, room_name):

    room = Room.objects.filter(name=room_name)
    if not room:
        room = Room.objects.create(name=room_name)
    else:
        room = room[0]

    rooms = Room.objects.all()
    messages = Message.objects.filter(room=room, is_bot=False).order_by('-timestamp').all()[:50]

    return render(request, 'chat/room.html', {
        'room_name_json': mark_safe(json.dumps(room_name)),
        'username': mark_safe(json.dumps(request.user.username)),
        'rooms': rooms,
        'messages': messages[::-1],
        'user': request.user
    })

def error404(request):
    return render(request, 'chat/404.html')

def error500(request):
    return render(request, 'chat/500.html')