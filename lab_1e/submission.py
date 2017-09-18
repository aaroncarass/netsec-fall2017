#!/usr/bin/python3
#
#
#

import sys 
import random
import asyncio


from playground.network.common import StackingProtocol, StackingProtocolFactory, StackingTransport

from playground.network.packet import PacketType
from playground.network.packet.fieldtypes import BOOL, UINT32, STRING, BUFFER
from playground.network.packet.fieldtypes.attributes import Optional


import playground



SimpleOperation = ['add', 'multiply']

Answers = [-1] * 100



class SimplePassThruServerProtocol(StackingProtocol):
	def __init__(self, higherProtocol = None):
		super().__init__(higherProtocol)
		self.transport = None
	

	def connection_made(self, transport):
		super().connection_made(transport)
		print("SimplePassThruServerProtocol connection_made()")
		self.transport = transport
		self.higherTransport = StackingTransport(self.transport)
		print(self.higherTransport)
	

	def connection_lost(self, reason = None):
		super().connection_lost(reason)
		print("SimplePassThruServerProtocol connection_lost()")
		self.higherProtocol().transport.close()
		self.higherProtocol().connection_lost(reason)
	

	def data_received(self, data):
		print("SimplePassThruServerProtocol data_received()")
		print("SimplePassThruServerProtocol", self.higherTransport)
		self.higherProtocol().data_received(data)



class SimplePassThruClientProtocol(StackingProtocol):
	def __init__(self, higherProtocol = None):
		super().__init__(higherProtocol)
		self.transport = None
	

	def connection_made(self, transport):
		super().connection_made(transport)
		print("SimplePassThruClientProtocol connection_made()")
		self.transport = transport
		self.higherTransport = StackingTransport(self.transport)
		print(self.higherTransport)
	

	def connection_lost(self, reason = None):
		super().connection_lost(reason)
		print("SimplePassThruClientProtocol connection_lost()")
		self.higherProtocol().transport.close()
		self.higherProtocol().connection_lost(reason)
	

	def data_received(self, data):
		print("SimplePassThruClientProtocol data_received()")
		print("SimplePassThruClientProtocol", self.higherTransport)
		self.higherProtocol().data_received(data)



def basicUnitTestQQQ():
	f = StackingProtocolFactory(
			lambda: SimplePassThruServerProtocol(),
			lambda: SimplePassThruClientProtocol())
	
	ptConnector = playground.Connector(protocolStack = f)
	playground.setConnector("passthrough", ptConnector)



#
#
# Lab 1(d)
#
#

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



def basicOperation(mode, run = 1):
	f = StackingProtocolFactory(
			lambda: SimplePassThruServerProtocol(),
			lambda: SimplePassThruClientProtocol())
	
	ptConnector = playground.Connector(protocolStack = f)
	playground.setConnector("passthrough", ptConnector)


	loop = asyncio.get_event_loop()

	if mode == "server":
		#
		# Changing over to create_playground_server() seems to cause
		# some unexplained packet loss.
		#
		coroServer = playground.getConnector("passthrough").create_playground_server(lambda: SimpleMathProtocolServer(), 8080)
		server = loop.run_until_complete(coroServer)

	else:
		coroClient = playground.getConnector().create_playground_connection(lambda: SimpleMathProtocolClient(), "20174.1.1.1", 8080)
		transport, protocol = loop.run_until_complete(coroClient)

		for i in range(0, int(run)):
			protocol.requestProblem()

	loop.run_forever()
	loop.close()



if __name__ == "__main__":
	if len(sys.argv) > 1:
		if sys.argv[1] == "server":
			basicOperation("server")
		else:
			if len(sys.argv) == 3:
				#
				# Should type check the second argument.
				#
				basicOperation("client", sys.argv[2])
			else:
				basicOperation("client", 10)
