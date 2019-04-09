from celery.signals import task_success
from .models import Message, Room

@task_success.connect
def task_success_handler(sender=None, result=None, **kargs):
    room = Room.objects.filter(name=result['message']['room'])[0]
    message = Message.objects.create(
        content=result['message']['content'],
        room=room,
        is_bot=True
    )