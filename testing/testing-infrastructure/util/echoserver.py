import socket, select, sys

def info():
    print "python echoserver.py <portnum>"
    print "  Sends back whatever's sent to it. portnum is the TCP port to echo."
    exit()


if __name__ == '__main__':
     
    if ((len(sys.argv) < 2) or
        (sys.argv[1] == "help") or
        (sys.argv[1] == "--help") or
        (sys.argv[1] == "-h") or
        (int(sys.argv[1]) > 2**16) or
        (int(sys.argv[1]) < 0)):
        info()
    
    CONNECTION_LIST = []# list of socket clients
    RECV_BUFFER = 4096 # Advisable to keep it as an exponent of 2
    PORT = int(sys.argv[1])

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # this has no effect, why ?
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('0.0.0.0', PORT))
    server_socket.listen(10)

    # Add server socket to the list of readable connections
    CONNECTION_LIST.append(server_socket)

    print 'Chat server started on port ' + str(PORT)

    while 1:
        # Get the list sockets which are ready to be read through select
        read_sockets,write_sockets,error_sockets = select.select(CONNECTION_LIST,[],[])

        for sock in read_sockets:
    
            #New connection
            if sock == server_socket:
                # Handle the case in which there is a new connection recieved through server_socket
                sockfd, addr = server_socket.accept()
                CONNECTION_LIST.append(sockfd)
                print 'Client (%s, %s) connected' % addr
            
            #Some incoming message from a client
            else:

                # Data recieved from client, process it
                try:
                    #In Windows, sometimes when a TCP program closes abruptly,
                    # a 'Connection reset by peer' exception will be thrown
                    data = sock.recv(RECV_BUFFER)
                    # echo back the client message
                    if data:
                        sock.send('OK ... ' + data)
    
                # client disconnected, so remove from socket list
                except:
                    broadcast_data(sock, 'Client (%s, %s) is offline' % addr)
                    print 'Client (%s, %s) is offline' % addr
                    sock.close()
                    CONNECTION_LIST.remove(sock)
                    continue
                
    server_socket.close()


