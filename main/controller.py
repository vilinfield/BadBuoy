#!/usr/bin/env python

from time import sleep  # Wait between commands
import threading  # Multi threading
from Phidgets.Devices.MotorControl import MotorControl  # Motor control
from Phidgets.Devices.AdvancedServo import AdvancedServo  # Servo control
from Phidgets.Devices.Servo import ServoTypes  # Servo type setting
import pygame  # General Pygame imports
from pygame import init as startPygame  # Initialize imported Pygame modules
from pygame import joystick, locals  # Logitech attack 3 joystick support
import tornado.web  # Tornado web framework
import tornado.ioloop  # I/O event loop for non-blocking sockets
import tornado.websocket  # Bi directional messages from server (this) to client (webpage)

# Motors and servo control boards
m1 = MotorControl()
m2 = MotorControl()
m3 = MotorControl()
s1 = AdvancedServo()

# Websocket list for storing values
wss = []

# Set motor acceleration
def setAllMotorsAcceleration(v):
    m1.setAcceleration(0, v)
    m1.setAcceleration(1, v)
    m2.setAcceleration(0, v)
    m2.setAcceleration(1, v)
    m3.setAcceleration(0, v)

# Tornado website application settings
def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),  # Main page
        (r"/websocket", wsHandler),  # Websocket support
        (r"/(.*)", tornado.web.StaticFileHandler, {'path':'static/'}),  # Static file support
    ])

# Start tornado (used for multithreading)
def tornado_runit():
    tornado.ioloop.IOLoop.current().start()

# Controller (the main part of the application)
# Moving the joystick axis or clicking certain buttons calls functions to
# move motors on the rov itself

def setVelocity(controllerObject, controllerIndex, motorIndex, value):
    controllerObject.setVelocity(value)
    wsSend("M" + str(controllerIndex) + str(index) + str(value))

def moveClaw():
    s1.setPosition(0, ((Joystick.get_axis(2) + 1) * 0.5) * servoScale)
    s1.setPosition(0, position

def moveLateral():
    velocity = Joystick.get_axis(0) * 100
    setVelocity(m1, 0, 0, velocity)
    setVelocity(m1, 0, 1, velocity)

def moveOpposite(multi):
    velocity = Joystick.get_axis(0) * 100 * nulti
    setVelocity(m1, 0, 0, velocity)
    setVelocity(m1, 0, 1, velocity * multi)

def moveVerts():
    velocity = Joystick.get_axis(1) * -100
    setVelocity(m2, 1, 0, velocity)
    setVelocity(m2, 1, 1, velocity)

def moveSpinman():
    velocity = Joystick.get_axis(1) * 100 * multi
    setVelocity(m3, 2, 0, velocity)

def main():
    while True:
        for e in pygame.event.get():
            if e.type == locals.JOYAXISMOTION:
                if Joystick.get_button(0): # Lateral
                    moveLateral()

                if Joystick.get_button(1): # Vertical Control
                    moveVerts()

                if Joystick.get_button(2): # Spinman
                    moveSpinman()

                if Joystick.get_button(3): # Turn Right
                    moveOpposite(-1)

                if Joystick.get_button(4): # Turn Left
                    moveOpposite(1)

                if Joystick.get_button(7) or Joystick.get_button(8):
                    moveClaw()

            elif e.type == locals.JOYBUTTONDOWN:
                if Joystick.get_button(5) and Joystick.get_button(6) and Joystick.get_button(9) and Joystick.get_button(10) == 1:
                    print ("Exiting...")  # Emergency stop / properly quit
                    wsSend("K")
                    sleep(0.05)
                    s1.setEngaged(0, False)
                    s1.closePhidget()
                    m1.closePhidget()
                    m2.closePhidget()
                    m3.closePhidget()
                    tornado.ioloop.IOLoop.instance().stop()
                    print ("Goodbye")
                    exit(1)

# Initialize pygame
startPygame()
joystick.init()

# Initialize motors and servo
try:
    print("Initializing motors and servo...")
    m1.openPhidget(serial=392573)
    m2.openPhidget(serial=393150)
    m3.openPhidget(serial=398770)
    s1.openPhidget(serial=99590)
    m1.waitForAttach(10000)
    m2.waitForAttach(10000)
    m3.waitForAttach(10000)
    s1.waitForAttach(10000)
    print("Done\n")
except Exception as e:
    print str(e)
    exit(1)

# Setup motors and servos
print("Setting up motors and servo...")
s1.setServoType(0, ServoTypes.PHIDGET_SERVO_HITEC_HS322HD)
s1.setEngaged(0, True)
s1.setAcceleration(0, s1.getAccelerationMax(0))
s1.setVelocityLimit(0, s1.getVelocityMax(0))
s1.setPosition(0, s1.getPositionMin(0))
setAllMotorsAcceleration(25)
servoScale = s1.getPositionMax(0) - s1.getPositionMin(0)
print("Done\n")

# Setup joystick
try:
    print("Setting up joystick...")
    Joystick = joystick.Joystick(0)
    Joystick.init()
    print("Connected to Joystick %s" % Joystick.get_id())
except Exception as e:
    print str(e)
    print("Error: No Joystick")
    exit(1)

# Websocket handler
class wsHandler(tornado.websocket.WebSocketHandler):
    def open(self):  # If websocket connection opens say so (means it's good to go)
        print("\nWebsocket online")
        if self not in wss:
            wss.append(self)

    def on_close(self):  # If websocket connection ends say so
        print("\nWebsocket offline")
        if self in wss:
            wss.remove(self)

# Send a websocket message to the client to be interputed by the main.js script
def wsSend(message):
    for ws in wss:
        if not ws.ws_connection.stream.socket:
            print("Web socket does not exist anymore!!!")
            wss.remove(ws)
        else:
            ws.write_message(message)

# Setup website using a template
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")

if __name__ == '__main__':
    print("\nStarting...\n")
    app = make_app()  # Start web server on localhost:23456
    app.listen(23456)
    tornadoThread = threading.Thread(target=tornado_runit) # Start tornado
    tornadoThread.start()
    print("\nStarted\n")
    main() # Start controller
