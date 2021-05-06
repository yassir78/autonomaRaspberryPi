import socketio
import time
sio = socketio.Client()

@sio.event
def connect():
    print('connection established')

@sio.event
def my_message(data):
    
    sio.emit('speed', {'response': data})

@sio.event
def disconnect():
    print('disconnected from server')

sio.connect('http://localhost:8080')
my_message(22)
sio.wait()
