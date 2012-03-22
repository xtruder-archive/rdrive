#!/usr/bin/env python

import pygame
import sys
import socket
import struct
from optparse import OptionParser
from bits import *
from datetime import *
from time import sleep

# allow multiple joysticks
joy = []
last_servo0=0
last_servo1=0

def SendServo(sock,id,pos,max):
    # convert joystick position to servo increment, 0-180
    move = round(pos * max, 0)
    # uncomment to debug
    print "Move val ", move
    val=int(abs(move))
    if (move > 0):
        val=setBit(val,4)
    #enable movement
    val=setBit(val,5)
    if id==1:
        #set to servo 2
        val=setBit(val,6)
    #pack to desired format
    send=struct.pack("!B",val)
    # uncomment to debug
    #print "Sent val ", repr(send)
    # and send over sockets
    try:
        sock.send(send)
    except socket.error, msg:
        print >>sys.stderr,"Socket error: ", msg
        return False
    
    return True

# handle joystick event
def handleJoyEvent(e, sock, m1, m2):
    if e.type == pygame.JOYAXISMOTION:
        axis = "unknown"
        if (e.dict['axis'] == 0):
            axis = "X"

        if (e.dict['axis'] == 1):
            axis = "Y"

        if (e.dict['axis'] == 2):
            axis = "Throttle"

        if (e.dict['axis'] == 3):
            axis = "Z"

        if (axis != "unknown"):
            str = "Axis: %s; Value: %f" % (axis, e.dict['value'])
            # uncomment to debug
            output(str, e.dict['joy'])

            pos = e.dict['value']
            # Arduino joystick-servo hack
            if (axis == "X"):
                global last_servo0
                last_servo0= pos
                if not SendServo(sock, 0, pos, m1):
                    return False
                
            # Arduino joystick-servo hack
            if (axis == "Y"):
                global last_servo1
                last_servo1= pos
                if not SendServo(sock, 1, pos, m2):
                    return False

    elif e.type == pygame.JOYBUTTONDOWN:
        str = "Button: %d" % (e.dict['button'])
        # uncomment to debug
        output(str, e.dict['joy'])
        # Button 0 (trigger) to quit
        if (e.dict['button'] == 0):
            print "Bye!\n"
            return False
    else:
        pass
    
    return True

# print the joystick position
def output(line, stick):
    #print "Joystick: %d; %s" % (stick, line)
    pass

# wait for joystick input
def joystickControl(sock, m1, m2):
    last_time= None
    while True:
        first_event= pygame.event.poll()
        if(first_event.type==pygame.NOEVENT):
            if last_time==None or (datetime.now()-last_time)>timedelta(microseconds=800000):
                if not SendServo(sock, 0, last_servo0, m1) or \
                   not SendServo(sock, 1, last_servo1, m2):
                    return
                last_time= datetime.now()
            continue
        events = [first_event]
        events.extend(pygame.event.get())
        for e in events:
            if (e.type == pygame.JOYAXISMOTION or e.type == pygame.JOYBUTTONDOWN):
                if handleJoyEvent(e, sock, m1, m2)==False:
                    return
                last_time= datetime.now()

# main method
def main():
    parser = OptionParser()
    parser.add_option("-i", "--ip", dest="ip",
                  help="IP address of car", type="string", default="127.0.0.1")
    parser.add_option("-p", "--port", dest="port",
                  help="Port of car", type="int", default=64100)
    parser.add_option("-1", "--max1", dest="m1",
                  help="Max value for servo 1", type="int", default=5)
    parser.add_option("-2", "--max2", dest="m2",
                  help="Max value for servo 2", type="int", default=10)
    (options, args) = parser.parse_args()
    
    # initialize pygame
    pygame.joystick.init()
    pygame.display.init()
    if not pygame.joystick.get_count():
        print "\nPlease connect a joystick and run again.\n"
        quit()
    print "\n%d joystick(s) detected." % pygame.joystick.get_count()
    for i in range(pygame.joystick.get_count()):
        myjoy = pygame.joystick.Joystick(i)
        myjoy.init()
        joy.append(myjoy)
        print "Joystick %d: " % (i) + joy[i].get_name()
    print "Depress trigger (button 0) to quit.\n"
    
    # connect to car
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error, msg:
            print >>sys.stderr,"Socket error: ", msg
            quit()
    try:       
        sock.connect((options.ip, int(options.port)))
    except socket.error, msg:
            print >>sys.stderr,"Socket error: ", msg
            sock.close()
            quit()
    # run joystick listener loop
    joystickControl(sock, int(options.m1), int(options.m2))
    
    sock.close()

# allow use as a module or standalone script
if __name__ == "__main__":
    main()
