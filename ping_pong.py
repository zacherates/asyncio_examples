"""
> python.exe ping_pong.py <command> <port> <args>*

eg.
	#starts server on port 8888
	python.exe ping_pong.py pong 8888

	#pings the server on port 8888
	python.exe ping_pong.py ping 8888

help: displays this message
pong <port>: starts the server
ping <port> [<count>]: ping the server <count> times.
"""

import asyncio
import sys
import textwrap

@asyncio.coroutine
def ponger(client_reader, client_writer):
	host, port, *_ = client_writer.get_extra_info('peername')
	print("client connected from:", (host, port))

	while True:
		bytes = yield from client_reader.read(4)
		if len(bytes) == 0:
			client_writer.close()
			break

		print("data recieved:", repr(bytes))
		client_writer.write("PONG".encode('utf-8'))

def pong(port):
	loop = asyncio.get_event_loop()
	coro = asyncio.start_server(ponger, 'localhost', port)
	server = loop.run_until_complete(coro)
	print('listening on {} (^C to exit)'.format(server.sockets[0].getsockname()[1]))
	try:
		loop.run_until_complete(waiter())
	except KeyboardInterrupt:
		print("exit")
	finally:
		server.close()
		loop.close()

@asyncio.coroutine
def waiter():
	while True:
		yield from asyncio.sleep(0.1)

@asyncio.coroutine
def pinger(route, count = 1):
	message = "PING"

	server_reader, server_writer = yield from asyncio.open_connection(*route)
	for i in range(count):
		print("-->", message)
		server_writer.write(message.encode())

		response = yield from server_reader.read(4)
		print("<--", response.decode())

	server_writer.close()
	
def ping(port, count = 1):
	loop = asyncio.get_event_loop()
	coro = pinger(('localhost', port), int(count))
	loop.run_until_complete(coro)
	loop.close()


commands = {
	'ping': ping,
	'pong': pong,
}

def main(script, command = 'help', port = 8888, *args):
	if command in commands:
		commands[command](int(port), *args)
	else:
		print(textwrap.dedent(__doc__))

if __name__ == "__main__":
	main(*sys.argv)
