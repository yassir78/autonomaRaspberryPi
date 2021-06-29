import numpy as np
import cv2
from picamera.array import PiRGBArray
import RPi.GPIO as GPIO
from threading import Thread
import socketio
import base64
import time

# Envoie des captures au serveur
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
def disconnect():
    print('disconnected from server')

sio.connect('https://autonomabackend.herokuapp.com/')

# Ouvrir la camera par defaut pour prendre une video
video_capture = cv2.VideoCapture(-1)
# cv::CAP_PROP_FRAME_WIDTH =3,
# 	Définir la largeur du frame dans la video
video_capture.set(3, 160)
# cv::CAP_PROP_FRAME_HEIGHT =4,
# Définir la hauteur du frame dans la video
video_capture.set(4, 120)

# setup GPIO pins
# Utilisation de la numérotation électronique de la puce
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(3, GPIO.OUT) #input 2 motor A
GPIO.setup(4, GPIO.OUT) #input 1 motor A
GPIO.setup(22, GPIO.OUT) #input 2 motor B
GPIO.setup(27, GPIO.OUT) #input 1 motor B


while(True):

 

    # Capture des frames
    # Retourne true si le frame a été lu correctement
    ret, frame = video_capture.read()

    # Rogner (crop) l'image

    crop_img = frame[30:60, 0:160]


    # Convertir la couleur d'une image :
    # parametre 1 l'image, parametre 2 le code de convertion
    gray = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)

    # Appliquer le flou gaussian
    # Pour réduire le bruit de l'image et réduire les détails

    blur = cv2.GaussianBlur(gray,(5,5),0)

    # Binarisation de l'image ( noir/blanc)
    # prmtr 1 : source (image gray)
    # prmtr 2: valeur seuil de binarisation
    # prmtr 3 : valeur max
    # prmtr 4 : type de binarisation
    ret,thresh = cv2.threshold(blur,60,255,cv2.THRESH_BINARY_INV)


    # Rechrche du contour de l'image
    # Utilisation d'une image binarisé pour une meilleure précision (accuracy)
    # prmtr 1 : copie de l'image source
    # prmtr 2 : mode recuperation de contours
    # prmtr 3 : methode d'approximation du contour
    # retourne listes des contours
    # Chaque contour est un tableau numpy(x,y)
    contours,hierarchy = cv2.findContours(thresh.copy(), 1, cv2.CHAIN_APPROX_NONE)

    # Convertir l'image en binary buffer pour l'envoyer au serveur
    res, frame = cv2.imencode('.png', frame)
    # convert to base64 format
    data = base64.b64encode(frame)
    image(data.decode('ascii'))
    

    # Trouver le contour de la ligne à suivre
    if len(contours) > 0:
        # retourne le contour qui a la surface maximale
        c = max(contours, key=cv2.contourArea)
        # Calcule de plusieurs mesure: surface, centre de masse d'objet ... etc.
        M = cv2.moments(c)

        # Récuperation du centre de masse d'objet
        cx = int(M['m10']/M['m00'])
        cy = int(M['m01']/M['m00'])

 
        # Dessiner une ligne vertical et une horizontal passant par le centre de l'objet
        cv2.line(crop_img,(cx,0),(cx,720),(255,0,0),1)

        cv2.line(crop_img,(0,cy),(1280,cy),(255,0,0),1)

 
        # Dessiner le contour
        cv2.drawContours(crop_img, contours, -1, (0,255,0), 1)

 
        print(cx)
        if cx >= 120:  # turn right
            GPIO.output(3, GPIO.LOW)
            GPIO.output(4, GPIO.LOW)
            GPIO.output(22, GPIO.HIGH)
            GPIO.output(27, GPIO.LOW) 
            
        if cx < 120 and cx > 50:
            speed(22)
            GPIO.output(22, GPIO.HIGH)
            GPIO.output(27, GPIO.LOW)
            GPIO.output(3, GPIO.HIGH)
            GPIO.output(4, GPIO.LOW) 
            
        if cx <= 50:  # turn left
            GPIO.output(22, GPIO.LOW)
            GPIO.output(27, GPIO.LOW)
            GPIO.output(3, GPIO.HIGH)
            GPIO.output(4, GPIO.LOW) 
            
             
           
    else:
            print("I don't see the line")

 

    #Afficher l'image capturée

    cv2.imshow('frame',crop_img)

    if cv2.waitKey(1) & 0xFF == ord('q'):

        break