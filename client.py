import socketio
import time
sio = socketio.Client()
@sio.event
def connect():
    print('connection established')
@sio.event
def speed(data):
    sio.emit('speed',{'response':data})
@sio.event
def image(data):
    sio.emit('data',{'response':data})
@sio.event
def direction(data):
    sio.emit('direction',{'response':data})
@sio.event
def disconnect():
    print('disconnected from server')

sio.connect('https://autonomabackend.herokuapp.com/')

