import numpy as np
import random
import logging
from copy import deepcopy
from typing import Union

from Transaction import Transaction
from Block import Block
from utils import expon_distribution
from Block import BlockChain
from DiscreteEventSim import simulation, Event


from config import RATE_PARAMETER, INITIAL_COINS
import config

logger = logging.getLogger(__name__)


class Link:
    def __init__(self, peer1: "Peer", peer2: "Peer"):
        self.peer1 = peer1
        self.peer2 = peer2
        # overall latency = ρij + |m|/cij + dij
        self.pij = random.uniform(10, 501)  # ms
        self.cij = 5 if peer1.is_slow_network or peer2.is_slow_network else 100  # Mbps
        self.cij = self.cij*1024/8*1000  # kB/ms

    def get_delay(self, message: Union[Transaction, Block]):
        dij = expon_distribution((96/8)/self.cij)  # ms
        return self.pij + message.size/self.cij + dij  # ms

    def __repr__(self):
        return f"Link({self.peer1}, {self.peer2})"

    def __eq__(self, other):
        return (self.peer1 == other.peer1 and self.peer2 == other.peer2) or (self.peer1 == other.peer2 and self.peer2 == other.peer1)

    def __hash__(self):
        return hash((self.peer1, self.peer2))


class Peer:

    def __init__(self, id, is_slow_network=False, is_slow_cpu=False):
        self.id: int = id
        self.is_slow_network: float = is_slow_network
        self.is_slow_cpu: float = is_slow_cpu
        self.crypto_coins: int = INITIAL_COINS
        self.neighbours: dict["Peer", Link] = {}
        self.cpu_power: float = self.__calculate_cpu_power()

        self.forwarded_messages: list[Union[Transaction, Block]] = []

    def __calculate_cpu_power(self) -> float:
        num_peers = config.NUMBER_OF_PEERS
        z1 = config.Z1
        deno = (10-9*z1)*num_peers
        neu = 1
        low_cpu_power = (neu/deno)
        return low_cpu_power if self.is_slow_cpu else 10*low_cpu_power

    def init_blockchain(self, peers: list["Peer"]):
        self.block_chain = BlockChain(cpu_power=self.cpu_power,
                                      broadcast_block_function=self.broadcast_block,
                                      peers=peers)

    def connect(self, peer: "Peer", link: Link):
        # self.connected_peers.append(peer)
        self.neighbours[peer] = link

    def disconnect(self, peer):
        # self.connected_peers.remove(peer)
        self.neighbours.pop(peer)

    def __str__(self) -> str:
        return f"Peer(id={self.id} cpu_power={self.cpu_power} is_slow_network={self.is_slow_network} is_slow_cpu={self.is_slow_cpu})"

    def __repr__(self):
        return f"Peer(id={self.id})"

    @property
    def connected_peers(self):
        return list(self.neighbours.keys())

    def create_txn(self, timestamp):
        to_peer = np.random.choice(self.connected_peers)
        amount = random.uniform(0, self.crypto_coins)
        self.crypto_coins -= amount
        return Transaction(self, to_peer, amount, timestamp)

    def broadcast_msg(self, msg: Union[Transaction, Block]):
        '''
        Broadcast a message to all connected peers.
        '''
        for peer in self.connected_peers:
            self.__forward_msg_to_peers(msg, peer)

    def __forward_msg_to_peers(self, msg: Union[Transaction, Block], peers: list["Peer"]):
        '''
        Forward a message to given peers.
        '''
        for peer in peers:
            self.__forward_msg_to_peer(msg, peer)

    def __transmit_msg(self, msg: Union[Transaction, Block], peer: "Peer"):
        '''
        Transmit a message to a peer.
        '''
        delay = self.neighbours[peer].get_delay(msg)
        event_type = "receive_txn" if isinstance(
            msg, Transaction) else "receive_block"
        new_event = Event(event_type, simulation.clock,
                          delay, peer.receive_msg, (msg, self), f"{self.id}->{peer.id}*; Δ:{delay}ms")
        simulation.enqueue(new_event)

    def __forward_msg_to_peer(self, msg: Union[Transaction, Block], peer: "Peer"):
        '''
        Forward a message to given peer.
        '''
        event_type = "send_txn" if isinstance(
            msg, Transaction) else "send_block"
        new_event = Event(event_type=event_type,
                          created_at=simulation.clock,
                          delay=0,
                          action=self.__transmit_msg,
                          payload=(msg, peer),
                          meta_description=f"{self.id}*->{peer.id};")
        simulation.enqueue(new_event)

    def receive_msg(self, msg: Union[Transaction, Block], source: "Peer"):
        '''
        Receive a message from another peer.
        validate the message
        forward the message to other peers if needed* avoid loop
        '''
        if msg in self.forwarded_messages:
            return

        if isinstance(msg, Transaction):
            self.block_chain.add_transaction(msg)
        else:
            # logger.debug(f"Received block: {str(msg)}")
            self.block_chain.add_block(msg)

        self.forwarded_messages.append(msg)

        self.__forward_msg_to_peers(
            msg, list(filter(lambda x: x != source, self.connected_peers)))

    def broadcast_txn(self, txn):
        '''
        Broadcast a transaction to all connected peers.
        '''
        # logger.info(f"Broadcasting transaction: {txn}")
        for peer in self.connected_peers:
            self.__forward_msg_to_peer(txn, peer)

    def broadcast_block(self, block: Block):
        '''
        Broadcast a block to all connected peers.
        '''
        for peer in self.connected_peers:
            self.__forward_msg_to_peer(block, peer)
