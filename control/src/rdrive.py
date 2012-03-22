import struct
import select, socket
import sys
import errno
from datetime import datetime

import lrc

def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)

status = enum('alive', 'connected', 'dead')
comma

ALIVE_DEADLINE= 3

class DeviceClient():
    def __init__(self, name, ip, port):
        self.name= name
        self.ip= ip
        self.port= port
        self.alive_time= datetime.now()
        self.s= None
        self.status= status.alive
        
    def connect(self):
        try:
            self.s= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.setblocking(0)
        except socket.error, msg:
            self.s= None
            print >>sys.stderr,"Socket error: ", msg
        try:
            self.s.connect((self.ip, self.port))
        except socket.error, msg:
            if msg[0]==errno.EINPROGRESS or msg[0]==errno.EISCONN:
                break
            else:
                self.s.close()
                print >>sys.stderr,"Connection to", self.ip, "error: ", msg
                
    def setConnected(self):
        self.status= status.connected
        
    def setAlive(self):
        self.alive_time= datetime.now()
        
    def isAlive(self):
        if (datetime.now()-self.alive_time)<ALIVE_DEADLINE:
            return True
        return False
    
    def ping(self, immediately=False):
        return True

class DeviceResolver():
    devices= []
    
    def __init__(self, port):
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except socket.error, msg:
            self.s= None
            print >>sys.stderr,"Socket error: ", msg
        try:
            self.s.bind(('<broadcast>', port))
            self.s.setblocking(0)
        except socket.error, msg:
            self.s.close()
            print >>sys.stderr,"Binding to UDP port " , str(port), " error: ", msg
        
    def ProcessBroadcast(self):
        readable, writable, exceptional = select.select([self.s],[],[], 0)
        for s in readable:
            (data,address)= s.recv(2)
            check, port, name= struct.unpack("!BHs", data)
            
            if(not lrc.checkLRC(port, check)):
                continue
            
            device= self.FindDeviceByAddress(address)
            if device:
                if(device.status==status.connected):
                    device.ping(True)
                device.setAlive()
            else
                devices.append(DeviceClient(name, address, port))
            
            '''#Signalize device to go to server mode
            data= struct.pack("!BB",check, 0x01)
            
            s.sendto(data, 0, address)'''
        #Exception on server
        for s in exceptional:
            self.s.close()
            return False
            
        return True
    
    def RemoveDeadDevices(self):
        remove=[]
        for device in self.devices:
            if      (device.status==status.dead) or \
                    (!device.isAlive()) or \
                    (device.status!=status.connected):
                remove.append(device)
        for device in remove:
            self.RemoveDevice(device)
            
    def ProcessDevices(self):
        pass
            
    def AddDevice(self, device):
        self.devices.append(device)
        
    def RemoveDevice(self, device):
        self.devices.remove(device)
        
    def FindDeviceByAddress(self, ip):
        for device in self.devices:
            if device.ip==ip:
                return device
        return None