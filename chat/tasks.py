from __future__ import absolute_import, unicode_literals
from celery import shared_task
import requests
from datetime import datetime


def message_to_json_bot(message_dict):
    try:
        headers = {'content-type': 'application/json'}
        response = requests.get('https://stooq.com/q/l/?s=aapl.us&f=sd2t2ohlcv&h&e=csv', headers=headers,
                                verify=True)
        if response.status_code == 200:
            data = response.text.split(',')
            symbol = data[7].split('\n')
            return {
                'content': '<b>' + message_dict['message'] + '</br>' + symbol[1] + ' quote is $%s</b>' % str(
                    data[-2]),
                'author': 'BOT',
                'timestamp': datetime.today().strftime("%b. %d, %Y, %I:%M %p"),
                'room': message_dict['room']
            }
        else:
            return {
                'content': '<b>' + message_dict['message'] + '</br>' + 'SERVICE ERROR:' + str(
                    response.status_code),
                'author': 'BOT',
                'timestamp': datetime.today().strftime("%b. %d, %Y, %I:%M %p"),
                'room': message_dict['room']
            }

    except Exception as e:
        return {
            'content': '<b>' + message_dict['message'] + '</br>' + 'ERROR:' + str(e),
            'author': 'BOT',
            'timestamp': datetime.today().strftime("%b. %d, %Y, %I:%M %p"),
            'room': message_dict['room']
        }

@shared_task
def add(data):
    #testing a sleep time and the chatroom is running well
    for i in range(100000):
        print(i)

    #task result
    return {
        'command': 'new_message',
        'message': message_to_json_bot(data)
    }
