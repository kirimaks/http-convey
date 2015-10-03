import sys
from urlparse import urlparse
import select
import socket

RECV_BS = 4096
TIME_OUT = 5

bad_urls = [ 'googleads.g.doubleclick.net', 
            'pagead2.googlesyndication.com',
            'tpc.googlesyndication.com',
            '94.198.53.135/b',
            'http://mh8.adriver.ru/images',
            'ad.adriver.ru/cgi-bin',
            'mg.dt00.net',
            '195.82.146.52/468x60/',
            '195.82.146.52/iframe',
            'imdj.3793369.pix-cdn.org/image/banner/',
            'imgg.marketgid.com',
            'c.marketgid.com',
            'ag-gb.marketgid.com',

            'www.olimpru.com',
            '195.82.146.52/728x90/0618_1.gif',


]

filtered_message = '''
<html>
<head>
</head>
<body>
    <h1>Filtered...</h1>
</body>
</html>
'''


def get_request(client_socket, raw_http):
    print raw_http.split('\n')[0]

    # Get host and port.
    request_uri = raw_http.split('\n')[0].split(' ')[1]
    port = 80
    url = urlparse(request_uri)
    rq_count = 0   # Request counter.


    #### Check for bad urls ####
    for a_url in bad_urls:
        if a_url in request_uri:
            print "\n[FILTERED]\n"
            client_socket.sendall(filtered_message)
            client_socket.close()
            return
    ####


    ###
    with open("/tmp/http_url.txt", "a") as out:
        out.write(request_uri)
        out.write('\n')
    ###


    # Connection.
    proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxy_socket.connect((url.netloc, port))
    proxy_socket.sendall(raw_http)

    cur_sockets = [proxy_socket, client_socket]

    while True:
        ready_read, ready_write, errors = select.select(cur_sockets, [], [], TIME_OUT)

        if not len(ready_read):
            proxy_socket.close()
            client_socket.close() # need to test!
            return
        
        for sock in ready_read:
            data = sock.recv(RECV_BS)

            if not len(data):
                cur_sockets.remove(sock)
                sock.close()

            else:
                # Show http response.
                if rq_count == 0: 
                    print data.split('\n')[0]
                    rq_count += 1

                # Read/Write
                if sock is proxy_socket:
                    print "<= [%d]" % len(data)
                    client_socket.sendall(data)

                else:
                    print "=> [%d]" % len(data)
                    proxy_socket.sendall(data)



# CONNECT linux.org.ru:443 HTTP/1.1

def connect_request(client_socket, raw_http):
    request_line = raw_http.split('\n')[0]

    print request_line

    host = request_line.split(' ')[1].split(':')[0]
    port = int(request_line.split(' ')[1].split(':')[1])

    proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxy_socket.connect((host, port))

    client_socket.sendall("HTTP/1.0 200 Connection established\r\nProxy-agent: proxy2.py\r\n\r\n")

    cur_sockets = [proxy_socket, client_socket]

    rq_count = 0   # Request counter.

    while True:
        ready_read, ready_write, errors = select.select(cur_sockets, [], [], TIME_OUT)

        if not len(ready_read):
            proxy_socket.close()
            client_socket.close() # need to test!
            return
        
        for sock in ready_read:
            data = sock.recv(RECV_BS)

            if not len(data):
                cur_sockets.remove(sock)
                sock.close()

            else:
                # Show http response.
                if rq_count == 0: 
                    #print data.split('\n')[0]
                    rq_count += 1

                # Read/Write
                if sock is proxy_socket:
                    print "<= [%d]" % len(data)
                    client_socket.sendall(data)

                else:
                    print "=> [%d]" % len(data)
                    proxy_socket.sendall(data)

    client_socket.close()

def unknown_request(client_socket, raw_http):
    print "[*** NOT IMPLEMENTED ***]\n%s" % raw_http
    client_socket.sendall('HTTP/1.1 501 Not Implemented\r\n\r\n')
    client_socket.close()

