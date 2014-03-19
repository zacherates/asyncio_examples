import random
import sys

import roulette

class Random(roulette.Router):
	def route(self, addr, data):
		return ('localhost', random.choice([8887, 8889]))

def main(script, port):
	roulette.start(Random(), int(port))

if __name__ == "__main__":
	main(*sys.argv)
