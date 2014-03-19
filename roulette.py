import asyncio

CHUNK_SIZE = 32 * 1024

class Router:
	@asyncio.coroutine
	def forward(self, from_, to):
		while True:
			bytes = yield from from_.read(CHUNK_SIZE)
			if len(bytes) == 0:
				to.close()
				return

			to.write(bytes)

	@asyncio.coroutine
	def listen(self, client_reader, client_writer):
		host, port, *_ = client_writer.get_extra_info('peername')
		print("client connected from:", (host, port))
		buffered = []

		while True:
			bytes = yield from client_reader.read(CHUNK_SIZE)
			buffered.append(bytes)
			route = self.route((host, port), b''.join(buffered))
			if route is not None:
				print("routing to:", route)
				(server_reader, server_writer) = yield from asyncio.open_connection(*route)
				server_writer.writelines(buffered)
				break

			if len(buffered[-1]) == 0:
				print("failed to route request")
				break

		yield from asyncio.wait([
			self.forward(client_reader, server_writer),
			self.forward(server_reader, client_writer),
		])

	def route(self, addr, data):
		raise NotImplemented

@asyncio.coroutine
def waiter():
	while True:
		yield from asyncio.sleep(0.1)

def start(router, port):
	loop = asyncio.get_event_loop()
	coro = asyncio.start_server(router.listen, 'localhost', port)
	server = loop.run_until_complete(coro)
	print('listening on {} (^C to exit)'.format(server.sockets[0].getsockname()[1]))

	try:
		loop.run_until_complete(waiter())
	except KeyboardInterrupt:
		print("exit")
	finally:
		server.close()
		loop.close()
