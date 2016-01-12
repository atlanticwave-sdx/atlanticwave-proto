# Copyright 2016 - Sean Donovan
#
# Test file for the cxnlib.py server-side code


from lib.cxnlib import *
from time import sleep

def printer_cb(obj):
    print "Received: " + str(obj)


server = AWConnection()
server.open_server_cxn()
client_connection, client_address = server.server_cxn_accept()
client_connection.register_receive_callback(printer_cb)
client_connection.start_receive_thread()

#print "client address: " + str(client_address)
client_connection.send({'a':4, 'b':5, 'c':{'z':6, 'y':7, 'x':8}})

#data = client_connection.recv()
#print "Received: " + str(data)



exit()
