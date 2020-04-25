# This script produces a log file for a workload. This workload is generated based on the parameters in all caps at the top of the file.
# To run, call like "python script_template.py <log name>"
# It will produce a file called <log name>
import json
from logging import basicConfig, getLogger, DEBUG
from pickle import dumps, loads
from random import choice, uniform
from socket import socket
from sys import argv
from time import sleep, monotonic
from typing import NamedTuple, Optional
from unittest.mock import patch

global NUM_NODES
NUM_NODES = 0

RAND_WORKLOAD_NUM_SOCKETS = 4
RAND_WORKLOAD_ITERATIONS = 50
RAND_WORKLOAD_BASE_ADDRESS = choice((30000, 40000, 50000, 60000))
RAND_WORKLOAD_CHANCE_SEND = 3
RAND_WORKLOAD_CHANCE_NOT_SEND = 2
RAND_WORKLOAD_ROUND_DELAY = 0.5  # seconds
RAND_WORKLOAD_MAX_CLOCK_DRIFT = 1.5  # seconds
RAND_WORKLOAD_CLOCK_DRIFTS = [uniform(-RAND_WORKLOAD_MAX_CLOCK_DRIFT, RAND_WORKLOAD_MAX_CLOCK_DRIFT) for _ in range(RAND_WORKLOAD_NUM_SOCKETS)]  # seconds


class HybridLogicalClock(NamedTuple('_hlc', (('physical', int), ('logical', int)))):
    __slots__ = ()

    def __new__(
        cls,
        physical: Optional[int] = None,
        logical: Optional[int] = None
    ) -> 'HybridLogicalClock':
        if None in (physical, logical) and (physical is not None or logical is not None):
            raise ValueError("You must provide both physical and logical, or neither. You can't supply only one.")
        else:
            if physical is None:
                physical = int(monotonic())
            physical = physical
            logical = logical or 0
        return super().__new__(cls, physical, logical)

    def update_on_event(self, id_) -> 'HybridLogicalClock':
        physical = max((self.physical, int(monotonic() + RAND_WORKLOAD_CLOCK_DRIFTS[id_])))
        if physical == self.physical:
            logical = self.logical + 1
        else:
            logical = 0
        return HybridLogicalClock(physical, logical)

    def update_on_message(self, id_, message: 'HybridLogicalClock') -> 'HybridLogicalClock':
        physical = max((self.physical, message.physical, int(monotonic() + RAND_WORKLOAD_CLOCK_DRIFTS[id_])))
        if physical in (self.physical, message.physical):
            logical = max((self, message)).logical + 1
        else:
            logical = 0
        return HybridLogicalClock(physical, logical)

    def __repr__(self) -> str:
        """Represent an HLC for easier debugging."""
        return f"HybridLogicalClock(physical={self.physical}, logical={self.logical})"

    def __int__(self) -> int:
        """Treat compsite timestamps as integers."""
        return self.composite



class FakeSocket:
    def __getattribute__(self, target):
        if target in ('sendto', 'recvfrom', 'socket', 'logger', 'peer_id', 'vc', 'hlc', 'id', 'accept', 'update_vc'):
            return super().__getattribute__(target)
        return getattr(super().__getattribute__('socket'), target)

    def __init__(self, *args, **kwargs):
        global NUM_NODES
        self.socket = socket(*args, **kwargs)
        self.hlc = HybridLogicalClock()
        self.peer_id = None
        self.id = NUM_NODES
        NUM_NODES += 1
        self.vc = [0] * NUM_NODES
        self.logger = getLogger(f"<Node {self.id}>")

    def update_vc(self, vc):
        prev_vc = self.vc
        size = max(NUM_NODES, len(vc))
        self.vc = [0] * size
        for idx in range(size):
            if len(prev_vc) > idx and len(vc) > idx:
                self.vc[idx] = max(prev_vc[idx], vc[idx])
            elif len(prev_vc) > idx:
                self.vc[idx] = prev_vc[idx]
            elif len(vc) > idx:
                self.vc[idx] = vc[idx]
            else:
                break

    def accept(self):
        self.logger.info("Receiving a connection. New node spawned.")
        return self.socket.accept()

    def sendto(self, msg, addr):
        self.vc[self.id] += 1
        self.hlc = self.hlc.update_on_event(self.id)
        info = (self.id, self.peer_id, self.vc, self.hlc, msg)
        self.peer_id = addr[1] - RAND_WORKLOAD_BASE_ADDRESS
        self.logger.info(json.dumps({
            "send": True,
            "recv": False,
            "from": self.id,
            "to": self.peer_id,
            "vc": self.vc,
            "hlc": self.hlc
        }))
        return self.socket.sendto(dumps(info), addr)

    def recvfrom(self, buff_size):
        raw, addr = self.socket.recvfrom(buff_size)
        info = loads(raw)
        self.peer_id, _, vc, hlc, msg = info
        self.vc[self.id] += 1
        self.update_vc(vc)
        self.hlc = self.hlc.update_on_message(self.id, hlc)
        self.logger.info(json.dumps({
            "send": False,
            "recv": True,
            "to": self.id,
            "from": self.peer_id,
            "vc": self.vc,
            "hlc": self.hlc
        }))
        return msg, addr


@patch('socket.socket', FakeSocket)
def main():
    # This is where you put your workloads
    basicConfig(filename=argv[-1], level=DEBUG)
    getLogger().info(
        "Random workload: num sockets: %r, num iterations: %r, base address: %r, chance of send: %r in %r, round delay (s): %r, max clock drift (s): %r, actual clock drifts: %r",
        RAND_WORKLOAD_NUM_SOCKETS,
        RAND_WORKLOAD_ITERATIONS,
        RAND_WORKLOAD_BASE_ADDRESS,
        RAND_WORKLOAD_CHANCE_SEND,
        RAND_WORKLOAD_CHANCE_SEND + RAND_WORKLOAD_CHANCE_NOT_SEND,
        RAND_WORKLOAD_ROUND_DELAY,
        RAND_WORKLOAD_MAX_CLOCK_DRIFT,
        RAND_WORKLOAD_CLOCK_DRIFTS
    )
    import socket
    servers = [socket.socket(type=socket.SOCK_DGRAM) for _ in range(RAND_WORKLOAD_NUM_SOCKETS)]
    for idx, server in enumerate(servers):
        server.bind(('localhost', RAND_WORKLOAD_BASE_ADDRESS + idx))
    randomizer = ([True] * RAND_WORKLOAD_CHANCE_SEND) + ([False] * RAND_WORKLOAD_CHANCE_NOT_SEND)
    for _ in range(RAND_WORKLOAD_ITERATIONS):
        flags = [0] * len(servers)
        for idx, sender in enumerate(servers):
            sender.update_vc([])  # just make sure it has the correct size
            if choice(randomizer):
                peer = sender
                while peer is sender:
                    peer = choice(servers)
                peer_idx = servers.index(peer)
                flags[peer_idx] += 1
                sender.sendto(b'', ('localhost', RAND_WORKLOAD_BASE_ADDRESS + peer_idx))
        sleep(RAND_WORKLOAD_ROUND_DELAY)
        for idx, receiver in enumerate(servers):
            while flags[idx]:
                flags[idx] -= 1
                receiver.recvfrom(4096)


if __name__ == '__main__':
    main()
