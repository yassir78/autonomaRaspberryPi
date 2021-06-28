#les imports
import socketio
import time
#creation d'une instance Socket.IO
sio = socketio.Client()

#cette methode est appele automatiquement une fois la connexion au serveur s'est etablit
@sio.event
def connect():
    print('connection established')
#cette methode permet d'envoyer les informations de la vitesse au serveur    
@sio.event
def speed(data):
    sio.emit('speed',{'response':data})
    
#cette methode permet d'envoyer les images de la camera au serveur    
@sio.event
def image(data):
    sio.emit('data',{'response':data})
    
#cette methode permet d'envoyer les informations directionnelles au serveur    
@sio.event
def direction(data):
    sio.emit('direction',{'response':data})
    
#le client peut se deconnecter du serveur via cette methode
@sio.event
def disconnect():
    print('disconnected from server')
    
#la connexion au serveur s'etablit via la methode connecte
sio.connect('https://autonomabackend.herokuapp.com/')

