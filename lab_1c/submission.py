#!/usr/bin/python3
#
#
#

import sys
import random
import asyncio


from playground.network.packet import PacketType
from playground.network.packet.fieldtypes import BOOL, UINT32, STRING, BUFFER
from playground.network.packet.fieldtypes.attributes import Optional

import playground



SimpleOperation = ['add', 'multiply']

Answers = [-1] * 100



class RequestMathQuestion(PacketType):
	DEFINITION_IDENTIFIER = "RMQ"
	DEFINITION_VERSION = "1.0" 

	FIELDS = [
			("Type", STRING)
			]


class MathQuestion(PacketType):
    DEFINITION_IDENTIFIER = "MQ"
    DEFINITION_VERSION = "1.0"

    FIELDS = [
            ("O1", UINT32),
            ("O2", UINT32({Optional:True})),
            ("Operation", STRING),
            ("ID", UINT32)
            ]


class MathSolution(PacketType):
    DEFINITION_IDENTIFIER = "MS"
    DEFINITION_VERSION = "1.0"

    FIELDS = [
            ("Solution", UINT32),
            ("ID", UINT32)
            ]


class MathResult(PacketType):
    DEFINITION_IDENTIFIER = "MR"
    DEFINITION_VERSION = "1.0"


    FIELDS = [
            ("Result", BOOL),
            ("ID", UINT32)
            ]


class MathError(PacketType):
    DEFINITION_IDENTIFIER = "ME"
    DEFINITION_VERSION = "1.0"


    FIELDS = [
            ("ID", UINT32)
            ]



def RI(MAX = 2**32):
	return random.randint(0, MAX - 1)



class SimpleMathProtocolServer(asyncio.Protocol):
	def __init__(self):
		self.transport = None


	def connection_made(self, transport):
		print("SimpleMathProtocolServer Connected to Client")
		self.transport = transport


	def data_received(self, data):
		self._deserializer = PacketType.Deserializer()
		self._deserializer.update(data)


		for p in self._deserializer.nextPackets():
			print("SimpleMathProtocolServer data_received()", p.DEFINITION_IDENTIFIER)
			if p.DEFINITION_IDENTIFIER == "RMQ":
				#
				# Problem Request
				# Assign ID for this connection
				#
				reply = MathQuestion()
				reply.ID = RI(len(Answers))

				if p.Type == "Simple":
					reply.O1 = RI(100)
					reply.O2 = RI(100)
					reply.Operation = random.choice(SimpleOperation)

				replySerialized = reply.__serialize__()




				if reply.Operation == "add":
					Answers[reply.ID] = reply.O1 + reply.O2
				elif reply.Operation == "multiply":
					Answers[reply.ID] = reply.O1 * reply.O2


				# print(reply.ID, reply.O1, reply.O2, reply.Operation, Answers[reply.ID])

				self.transport.write(replySerialized)

			elif p.DEFINITION_IDENTIFIER == "MS":
				res = MathResult()
				res.ID = p.ID

				res.Result = (Answers[res.ID] == p.Solution)
				resSerialized = res.__serialize__()

				if res.Result:
					print("SimpleMathProtocolServer Solved problem with ID", p.ID, "correctly")
				else:
					print("")
					print("SimpleMathProtocolServer Solved problem with ID", p.ID, "incorrectly!!!")
					print("")

				self.transport.write(resSerialized)


			elif p.DEFINITION_IDENTIFIER == "ME":
				#
				# Some error occured, I just close on it.
				#
				self.transport.close()

			else:
				print(p.DEFINITION_IDENTIFIER)
				print("WTF")
				self.transport.close()
				

	def connection_lost(self, exc):
		self.transport = None
		print("SimpleMathProtocolServer Lost Connection to Client")



class SimpleMathProtocolClient(asyncio.Protocol):
	def __init__(self):
		self.transport = None
	

	def requestProblem(self):
		prob = RequestMathQuestion()
		prob.Type = "Simple"

		probSerialized = prob.__serialize__()
		self.transport.write(probSerialized)


	def connection_made(self, transport):
		print("SimpleMathProtocolClient Connected to Server")
		self.transport = transport


	def data_received(self, data):
		self._deserializer = PacketType.Deserializer()
		self._deserializer.update(data)

		for p in self._deserializer.nextPackets():
			print("SimpleMathProtocolClient data_received()", p.DEFINITION_IDENTIFIER)
			if p.DEFINITION_IDENTIFIER == "MQ":
				sol = MathSolution()
				sol.ID = p.ID

				if p.Operation == "add":
					sol.Solution = p.O1 + p.O2
				elif p.Operation == "multiply":
					sol.Solution = p.O1 * p.O2

				solSerialized = sol.__serialize__()
				self.transport.write(solSerialized)
				# print(sol.ID, p.O1, p.O2, p.Operation, sol.Solution)

			elif p.DEFINITION_IDENTIFIER == "MR":
				if p.Result:
					print("SimpleMathProtocolClient Solved problem with ID", p.ID, "correctly")
				else:
					print("")
					print("SimpleMathProtocolClient Solved problem with ID", p.ID, "incorrectly!!!")
					print("")

			elif p.DEFINITION_IDENTIFIER == "ME":
				#
				# Some error occured, I just close on it.
				#
				self.transport.close()

			else:
				print(p.DEFINITION_IDENTIFIER)
				print("WTF")
				self.transport.close()

	
	def connection_lost(self, exc):
		self.transport = None
		print("SimpleMathProtocolClient Lost Connection to Server")



def basicUnitTestNonMockTransport():
	loop = asyncio.get_event_loop()

	coroServer = loop.create_server(lambda: SimpleMathProtocolServer(), port = 8080)
	server = loop.run_until_complete(coroServer)


	coroClient = loop.create_connection(lambda: SimpleMathProtocolClient(), host = "127.0.0.1", port = 8080)
	transport, protocol = loop.run_until_complete(coroClient)

	for i in range(0, 10):
		protocol.requestProblem()
	
	loop.run_forever()
	loop.close()



def basicUnitTest():
	from playground.network.testing import MockTransportToProtocol as MTP
	from playground.network.testing import MockTransportToStorageStream as MTSS

	from playground.asyncio_lib.testing import TestLoopEx


	loop = asyncio.set_event_loop(TestLoopEx())


	clientProtocol = SimpleMathProtocolClient()
	serverProtocol = SimpleMathProtocolServer()


	transportToServer, transportToClient = MTP.CreateTransportPair(clientProtocol, serverProtocol)


	clientProtocol.connection_made(transportToServer)
	serverProtocol.connection_made(transportToClient)

	for i in range(0, 10):
		clientProtocol.requestProblem()
		#
		# Testing is really done in the "brain" of
		# SimpleMathProtocolServer().
		#



def basicOperation(mode, run = 1):
	loop = asyncio.get_event_loop()

	if mode == "server":
		coroServer = loop.create_server(lambda: SimpleMathProtocolServer(), port = 8080)
		server = loop.run_until_complete(coroServer)

	else:
		coroClient = loop.create_connection(lambda: SimpleMathProtocolClient(), host = "127.0.0.1", port = 8080)
		transport, protocol = loop.run_until_complete(coroClient)
		for i in range(0, int(run)):
			protocol.requestProblem()

	loop.run_forever()
	loop.close()



if __name__ == "__main__":
	if len(sys.argv) == 1:
		basicUnitTest()
	elif len(sys.argv) > 1:
		if sys.argv[1] == "server":
			basicOperation("server")
		else:
			if len(sys.argv) == 3:
				basicOperation("client", sys.argv[2])
			else:
				basicOperation("client", 10)

