#!/usr/bin/env python2
#-*- coding: utf-8 -*-

import socket
import thread
import rq_handlers as rh

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(('localhost', 8888))
server_socket.listen(20)

def new_connection(client_socket):

    # First need to get http method.
    http_rq = client_socket.recv(rh.RECV_BS)

    method = http_rq.split('\n')[0].split(' ')[0]

    if method == "GET" or method == "POST":
        rh.get_request(client_socket, http_rq)

    elif method == "CONNECT":
        rh.connect_request(client_socket, http_rq)

    else:
        client_socket.sendall("HTTP/1.1 501 Not Implemented\r\n\r\n")


    client_socket.close()
    print "Connection done..."


while True:
    client_socket, addr = server_socket.accept()
    print "New connection: %s:%s" % (addr[0], addr[1])
    thread.start_new_thread(new_connection, (client_socket,))
