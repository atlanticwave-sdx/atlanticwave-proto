# Copyright 2019 - Sean Donovan
# AtlanticWave/SDX Project

# This is a REST interface to an anonymous FTP client Uses the ftplib
# Borrowing heavily from the following tutorials:
#   https://pythonprogramming.net/ftp-transfers-python-ftplib/
#   https://stackoverflow.com/questions/111954/using-pythons-ftplib-to-get-a-directory-listing-portably

from flask import Flask, jsonify, abort, make_response, request
from flask_restful import Api, Resource, reqparse, fields, marshal
from threading import Thread
from ftplib import FTP, error_perm
from time import sleep
from datetime import datetime
import sys



errors = {
    'NotFound': {
        'message': "A resource with that ID does not exist.",
        'status': 404,
        'extra': "No extra information",
    },
}


# HTTP status codes:
HTTP_GOOD           = 200
HTTP_CREATED        = 201
HTTP_ACCEPTED       = 202
HTTP_NO_CONTENT     = 204
HTTP_NOT_MODIFIED   = 304
HTTP_BAD_REQUEST    = 400
HTTP_FORBIDDEN      = 403     # RETURNED BY FLASK-RESTFUL ONLY
HTTP_NOT_FOUND      = 404
HTTP_NOT_ACCEPTABLE = 406
HTTP_CONFLICT       = 409
HTTP_SERVER_ERROR   = 500     # RETURNED BY FLASK-RESTFUL ONLY

# In progress status
IP_NO_TRANSFER        = "No Transfer"
IP_STARTED_TRANSFER   = "Started Transfer"
IP_TRANSFER_COMPLETE  = "Transfer Complete"
IP_TRANSFER_FAILED    = "Transfer Failed"

global in_progress
global total_time
global transfer_thread

in_progress = IP_NO_TRANSFER
total_time = None
api_process = None
transfer_thread = None

class DTNRequest(Resource):
    #global in_progress
    #def __init__(self, urlbase):
    #    self.urlbase = urlbase
        
    def post(self, remote, filename):
        global in_progress
        global total_time
        global transfer_thread
        print("DTNRequest for %s:%s" % (remote,filename))
        self.remote = remote
        self.filename = filename

        # Initialize IP_NO_TRANSFER and total_time
        in_progress = IP_NO_TRANSFER
        total_time = None

        # Kick off transfer thread
        transfer_thread = Thread(target=run_transfer_thread,
                                 args=(self.remote, self.filename))
        transfer_thread.daemon = True
        transfer_thread.start()

        # Watch the in_progress for changes
        while(in_progress == IP_NO_TRANSFER):
            print("in_progress hasn't changed yet. %s" % in_progress)
            sleep(.1)

        # Once we have a changed status, return corresponding change
        if in_progress == IP_STARTED_TRANSFER:
            # good!
            retval = {'state': 'Started transfer of %s' % filename,
                      'remote': remote,
                      'filename': filename}, HTTP_GOOD
        else:
            retval = {'state': 'FAILURE: %s' % in_progress}, HTTP_BAD_REQUEST

        return retval


def run_transfer_thread(remote, filename):
    global in_progress
    global total_time
    # Get start time
    start_time = datetime.now()
    
    # Get connection with FTP
    ftp = FTP(remote)
    ftp.login(user='anonymous', passwd='')
    
    # Verify file exists and set in_progress to correct result
    files = []
    try:
        files = ftp.nlst()
    except error_perm as resp:
        if str(resp) == "550 No files found":
            print("No files in this directory")
            in_progress = IP_TRANSFER_FAILED
            return
        else:
            print("Some other error occurred: %s" % str(resp))
            in_progress = IP_TRANSFER_FAILED
            return
    if filename not in files:
        print("File is not available %s" % files)
        in_progress = IP_TRANSFER_FAILED
        return
        
    in_progress = IP_STARTED_TRANSFER
        
    # Get file from remote connection
    localfile = open(filename, 'wb')
    ftp.retrbinary('RETR ' + filename, localfile.write, 1024)
    print("File %s has been transferred" % filename)
    

    # Set total_time to correct result
    end_time = datetime.now()
    total_time = str(end_time - start_time)
    in_progress = IP_TRANSFER_COMPLETE
    return
        

class Dir(Resource):
    def get(self, remote):
        # Get connection with FTP
        print("Dir GET: %s" % remote)
        ftp = FTP(remote)
        ftp.login(user='anonymous', passwd='')
    
        # Get the list of files
        files = []
        try:
            files = ftp.nlst()
        except error_perm as resp:
            if str(resp) == "550 No files found":
                print("No files in this directory")
                return("No files in this directory")
            else:
                print("Some other error occurred: %s" % str(resp))
                return("Some other error occurred: %s" % str(resp))
        print("Returning the following file list: %s" % files)
        return (str(files))

class Status(Resource):
    #def __init__(self, urlbase):
    #    self.urlbase = urlbase

    def get(self):
        global in_progress
        global total_time
        print("Status GET")
        retval = ("%s-%s" % (in_progress, total_time))
        print("GET status: %s" % retval)
        return retval




if len(sys.argv) < 3:
    print("Need two arguments:")
    print("  hostip - IP of current host")
    print("  port   - port on host to listen to")
    exit()
host = sys.argv[1]
port = sys.argv[2]
print("HOST: %s" % host)
print("PORT: %s" % port)

app = Flask(__name__)
api = Api(app, errors=errors)
api.add_resource(DTNRequest,
                 '/dtn/transfer/<string:remote>/<string:filename>',
                 endpoint='transfer',)
                 #resource_class_kwargs={'urlbase':urlbase})
api.add_resource(Dir,
                 '/dtn/transfer/<string:remote>',
                 endpoint='dir',)
                 #resource_class_kwargs={'urlbase':urlbase})
api.add_resource(Status,
                 '/dtn/status',
                 endpoint='status',)
                 #resource_class_kwargs={'urlbase':self.urlbase})

app.run(host=host, port=port)


