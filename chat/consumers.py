from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json
from .models import Message, Room
from django.contrib.auth import get_user_model
import requests
from datetime import datetime

from .tasks import add

User = get_user_model()


class ChatConsumer(WebsocketConsumer):

    def messages_to_json(self, messages):
        result = []
        for m in messages:
            result.append(self.message_to_json(m))
        return result

    def message_to_json(self, message):
        return {
            'content': message.content,
            'author': message.author.username if message.author else 'BOT',
            'timestamp': message.timestamp.strftime("%b. %d, %Y, %I:%M %p"),
            'room': message.room.name
        }


    #bot direct, the ascync bot is in listener of celery
    def message_to_json_bot(self, message_dict):
        try:
            headers = {'content-type': 'application/json'}
            response = requests.get('https://stooq.com/q/l/?s=aapl.us&f=sd2t2ohlcv&h&e=csv', headers=headers,
                                    verify=True)
            if response.status_code == 200:
                data = response.text.split(',')
                symbol = data[7].split('\n')
                return {
                    'content': '<b>COMMAND FROM ' + message_dict['from'] + ': ' + message_dict['message'] + '</br>' +
                               symbol[1] + ' quote is $%s</b>' % str(
                        data[-2]),
                    'author': 'BOT',
                    'timestamp': datetime.today().strftime("%b. %d, %Y, %I:%M %p"),
                    'room': message_dict['room']
                }
            else:
                return {
                    'content': '<b>COMMAND FROM ' + message_dict['from'] + ': ' + message_dict[
                        'message'] + '</br>' + 'SERVICE ERROR:' + str(
                        response.status_code),
                    'author': 'BOT',
                    'timestamp': datetime.today().strftime("%b. %d, %Y, %I:%M %p"),
                    'room': message_dict['room']
                }

        except Exception as e:
            return {
                'content': '<b>COMMAND FROM ' + message_dict['from'] + ': ' + message_dict[
                    'message'] + '</br>' + 'ERROR:' + str(e),
                'author': 'BOT',
                'timestamp': datetime.today().strftime("%b. %d, %Y, %I:%M %p"),
                'room': message_dict['room']
            }


    def fetch_messages(self, data):
        messages = Message.last_50_messages()
        content = {
            'messages': self.messages_to_json(messages)
        }

        self.send_message(content)

    def new_message(self, data):
        if data['message']:
            author = data['from']
            author_user = User.objects.filter(username=author)[0]
            room = Room.objects.filter(name=data['room'])[0]

            # load bot messages
            for m in Message.objects.filter(room=room, is_bot=True, read=False).order_by('-timestamp').all():
                Message.objects.filter(pk=m.id).update(read=True)
                content = {
                    'command': 'new_message',
                    'message': self.message_to_json(m)
                }
                self.send_chat_message(content)

            if data['message'] == '/stock=APPL':
                data['message'] = 'COMMAND FROM ' + data['from'] + ': ' + data['message']
                #delay the task in background
                add.delay(data)
            # create chat normal message
            else:
                message = Message.objects.create(
                    author=author_user,
                    content=data['message'],
                    room=room
                )
                content = {
                    'command': 'new_message',
                    'message': self.message_to_json(message)
                }
                self.send_chat_message(content)



    commands = {
        'fetch_messages': fetch_messages,
        'new_message': new_message
    }

    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        data = json.loads(text_data)
        self.commands[data['command']](self, data)

    # Receive message from WebSocket
    def send_chat_message(self, message):
        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Receive message from room group
    def chat_message(self, event):
        message = event['message']

        self.send(text_data=json.dumps(message))


    def send_message(self, message):
        self.send(text_data=json.dumps(message))