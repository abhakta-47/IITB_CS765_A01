import logging
import random
from time import sleep

from Peer import Peer
from network import is_connected, draw_graph, create_network
from DiscreteEventSim import simulation, Event
from utils import expon_distribution

from config import NUMBER_OF_PEERS, RATE_PARAMETER

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s')
logger = logging.getLogger(__name__)

n = NUMBER_OF_PEERS # number of peers


while True:
    peers = create_network(n)
    if is_connected(peers):
        break

# print(peers)
for peer in peers:
    logger.info(f"peer id: {peer.id}, neighbours: {peer.connected_peers}")
logger.info(is_connected(peers)) # should be False

while True:
    # Generate exponential random variable for interarrival time
    interarrival_time = expon_distribution(RATE_PARAMETER)
    from_peer = random.choice(peers)
    new_txn = from_peer.create_txn(simulation.clock)
    new_txn_event = Event("broadcast_transaction", simulation.clock, interarrival_time, from_peer.broadcast_txn, (new_txn,))
    simulation.enqueue(new_txn_event)
    sleep(1)