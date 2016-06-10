#!/usr/bin/python
import jrpc

server = None
server = jrpc.service.SocketProxy(50021) #The server's listening port
print server.echo("Hello World!")
