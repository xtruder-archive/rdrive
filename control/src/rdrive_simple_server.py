#!/usr/bin/python

import socket
import threading
import SocketServer
import struct
import smbus
import sys
from time import sleep
from optparse import OptionParser

import daemon

def bin(s):
    return str(s) if s<=1 else bin(s>>1) + str(s&1)

class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):
    def handle(self):
	print "New connection from:", self.client_address[0]
        bus= smbus.SMBus()
        bus.open(0)
	zero=0
        while True:
            if zero>10:
                break
            try:
                data = self.request.recv(1)
            except socket.error, msg:
                print >>sys.stderr,"Socket error: ", msg
                break
            if len(data)==0:
		zero+=1
                continue
	    zero=0
            value= struct.unpack("!B",data)
            #print "Val: ", bin(value[0])
            bus.write_byte(0x20,int(value[0]))
        bus.close()

	print "Connection from", self.client_address[0], "closed."

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

def client(ip, port, message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    sock.send(message)
    response = sock.recv(1024)
    print "Received: %s" % response
    sock.close()

def start(HOST, PORT):                                                       
    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    ip, port = server.server_address               
    server.allow_reuse_address=True
                                                                 
    # Start a thread with the server -- that thread will then start one
    # more thread for each request                          
    server_thread = threading.Thread(target=server.serve_forever)
    # Exit the server thread when the main thread terminates
    server_thread.setDaemon(True)
    server_thread.start()
    print "Server loop running in thread:", server_thread.getName()," on ip", ip, "and port", str(port)
                           
    while True:                               
        try:                                                                 
            sleep(10)                             
        except KeyboardInterrupt:                               
            server.shutdown()                         
            print "Bye!"                                                       
            break

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-i", "--ip", dest="ip",
                  help="IP address of car", type="string", default="0.0.0.0")
    parser.add_option("-p", "--port", dest="port",
                  help="Port of car", type="int", default=64100)
    parser.add_option("-d", "--daemon", dest="daemon",
                  help="Deamonize process", action="store_true", default=False)
    (options, args) = parser.parse_args()
    # Port 0 means to select an arbitrary unused port
    HOST, PORT = options.ip, options.port

    if options.daemon:
        with daemon.DaemonContext():
            start(HOST, PORT)
    else:
        start(HOST,PORT)
