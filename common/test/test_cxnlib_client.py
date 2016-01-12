# Copyright 2016 - Sean Donovan
#
# Test file for the cxnlib.py client-side code


from common.cxnlib import *
from time import sleep

def printer_cb(obj):
    print "Received: " + str(obj)

client = AWConnection()
client.register_receive_callback(printer_cb)
client.open_client_cxn()
client.start_receive_thread()

print "before send"
client.send({'a':1, 'b':2, 'c':{'z':9, 'y':8, 'x':7}})
print "after send" 

sleep (1)
exit()
