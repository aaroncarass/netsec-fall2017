#!/usr/bin/python3
#
#
#

import random


from playground.network.packet import PacketType
from playground.network.packet.fieldtypes import BOOL, UINT32, STRING, BUFFER


class RequestMathQuestion(PacketType):
    DEFINITION_IDENTIFIER = "RMQ"
    DEFINITION_VERSION = "1.0"


class MathQuestion(PacketType):
    DEFINITION_IDENTIFIER = "MQ"
    DEFINITION_VERSION = "1.0"

    FIELDS = [
            ("O1", UINT32),
            ("O2", UINT32),
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


def basicUnitTest():
    #
    # p1 is a packet of type RequestMathQuestion()
    #
    # t1 is the test deserialized equivalent packet of p1
    #
    p1 = RequestMathQuestion()

    p1b = p1.__serialize__()

    t1 = RequestMathQuestion.Deserialize(p1b)

    assert p1 == t1



    #
    # p2 is a packet of type MathQuestion()
    #
    # t2 is the test deserialized equivalent packet of p2
    #
    p2 = MathQuestion()
    p2.O1 = random.randint(0, 2^32)
    p2.O2 = random.randint(0, 2^32)
    p2.Operation = "add"
    p2.ID = random.randint(0, 2^32)

    p2b = p2.__serialize__()

    t2 = MathQuestion.Deserialize(p2b)

    assert p2 == t2



    #
    # p3 is a packet of type MathSolution()
    #
    # t3 is the test deserialized equivalent packet of p3
    #
    p3 = MathSolution()
    p3.Solution = random.randint(0, 2^32)
    p3.ID = random.randint(0, 2^32)

    p3b = p3.__serialize__()

    t3 = MathSolution.Deserialize(p3b)

    assert p3 == t3


    #
    # p4 is a packet of type MathResult()
    #
    # t4 is the test deserialized equivalent packet of p4
    #
    p4 = MathResult()
    p4.Result = bool(random.getrandbits(1))
    p4.ID = random.randint(0, 2^32)

    p4b = p4.__serialize__()

    t4 = MathResult.Deserialize(p4b)

    assert p4 == t4



if __name__ == "__main__":
    basicUnitTest()

