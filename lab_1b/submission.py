#!/usr/bin/python3
#
#
#

import random


from playground.network.packet import PacketType, FIELD_NOT_SET
from playground.network.packet.fieldtypes import BOOL, UINT32, STRING, BUFFER
from playground.network.packet.fieldtypes import StringFieldType
from playground.network.packet.fieldtypes.attributes import Optional


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



def testPacketType(pt):
	packet = pt()

	if packet.DEFINITION_IDENTIFIER == "RMQ":
		packet.Type = "Problem"
	elif packet.DEFINITION_IDENTIFIER == "MQ":
		packet.O1 = RI()
		packet.O2 = RI()
		packet.Operation = "add"
		packet.ID = RI()
	elif packet.DEFINITION_IDENTIFIER == "MS":
		packet.Solution = random.randint(0, 2**32)
		packet.ID = RI()
	elif packet.DEFINITION_IDENTIFIER == "MR":
		packet.Result = bool(random.getrandbits(1))
		packet.ID = RI()
	elif packet.DEFINITION_IDENTIFIER == "ME":
		packet.ID = RI()


	packetByte = packet.__serialize__()
	testPacket = pt().Deserialize(packetByte)

	assert packet == testPacket



def RI(MAX = 2**32):
	return random.randint(0, MAX - 1)



def basicUnitTest():
	for i in range(1, (2**5)):
		testPacketType(RequestMathQuestion)
		testPacketType(MathQuestion)
		testPacketType(MathSolution)
		testPacketType(MathResult)
		testPacketType(MathError)



if __name__ == "__main__":
	basicUnitTest()

