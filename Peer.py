import numpy as np
import random
import logging

from Transaction import Transaction
from utils import expon_distribution
from DiscreteEventSim import simulation, Event


from config import RATE_PARAMETER, INITIAL_COINS

logger = logging.getLogger(__name__)

class Link:
    def __init__(self, peer1, peer2):
        self.peer1 = peer1
        self.peer2 = peer2
        # overall latency = ρij + |m|/cij + dij 
        self.pij = random.uniform(10,501) # ms
        self.cij = 5 if peer1.is_slow or peer2.is_slow else 100 # Mbps
    
    def __delay(self, message):
        message_size = len(message)
        dij = expon_distribution(96) # 96 kb ms
        return self.pij + message_size/self.cij + dij

    def transmit(self, message):
        delay = self.__delay(message)
        # transmit

    def __repr__(self):
        return f"Link({self.peer1}, {self.peer2})"

    def __eq__(self, other):
        return (self.peer1 == other.peer1 and self.peer2 == other.peer2) or (self.peer1 == other.peer2 and self.peer2 == other.peer1)

    def __hash__(self):
        return hash((self.peer1, self.peer2))

class Peer:
    id: int
    is_slow: bool
    connected_peers: list["Peer"]
    crypto_coins: int

    def __init__(self, id, is_slow=False):
        self.id = id
        self.is_slow = is_slow
        self.connected_peers = []
        self.crypto_coins = INITIAL_COINS

    def connect(self, peer):
        self.connected_peers.append(peer)
        
    def disconnect(self, peer):
        self.connected_peers.remove(peer)
    
    def __repr__(self):
        return f"Peer(id={self.id})"
    
    def create_txn(self, timestamp):
        to_peer = np.random.choice(self.connected_peers)
        amount = random.uniform(0, self.crypto_coins)
        self.crypto_coins -= amount
        return Transaction(self, to_peer, amount, timestamp)
    
    def gen_txns(self):
        pass
        # time_since_last_transaction = 0
        # while True:
        #     # Generate exponential random variable for interarrival time
        #     interarrival_time = expon_distribution(RATE_PARAMETER)            
        #     # Update time_since_last_transaction for the next iteration
        #     new_txn = self.create_txn(time_since_last_transaction)
        #     new_txn_event = Event("broadcast_transaction", simulation.clock, interarrival_time, self.broadcast_txn, (new_txn,))
        #     simulation.enqueue(new_txn_event)            

    def __forward_txn_to_peer(self, txn:Transaction, peer:"Peer"):
        '''
        Forward a transaction to given peer.
        '''
        new_event = Event("receive_transaction", simulation.clock, 0, peer.receive_txn, (txn, ))
        simulation.enqueue(new_event)

    def broadcast_txn(self, txn):
        '''
        Broadcast a transaction to all connected peers.
        '''
        logger.info(f"Broadcasting transaction: {txn}")
        for peer in self.connected_peers:
            self.__forward_txn_to_peer(txn, peer)

    def forward_txn(self, txn):
        '''
        Forward a transaction to other peer.
        '''
        pass
    
    def __receive_txn(self, txn):
        '''
        Receive a transaction from another peer.
        validate the transaction
        forward the transaction to other peers if needed* avoid loop
        '''
        pass
    
    def receive_txn(self, txn):
        '''
        Receive a transaction from another peer.
        validate the transaction
        forward the transaction to other peers if needed* avoid loop
        '''
        logger.info(f"Received transaction: {self.id} {txn.txn_id}")


