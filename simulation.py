from config import NUMBER_OF_PEERS, RATE_PARAMETER, NUMBER_OF_TRANSACTIONS
import logging
import random
from time import sleep
import json
import yaml
import pickle

from Peer import Peer
from network import is_connected, draw_graph, create_network
from DiscreteEventSim import simulation, Event, EventType
from utils import expon_distribution
from Block import Block
from logger import init_logger

logger = init_logger()


def log_peers(peers):
    # print(peers)
    for peer in peers:
        logger.info("peer: %s", peer)
        logger.info("peer id: %s, neighbours: %s",
                    peer.id, peer.connected_peers)
    logger.info(is_connected(peers))


def schedule_transactions(peers):
    '''
    Schedule transactions
    '''
    time = 0
    while simulation.event_queue.qsize() <= NUMBER_OF_TRANSACTIONS:
        # Generate exponential random variable for interarrival time
        interarrival_time = expon_distribution(RATE_PARAMETER)
        # logger.debug(f"Interarrival time: {interarrival_time}")
        from_peer = random.choice(peers)
        new_txn = from_peer.create_txn(simulation.clock)
        new_txn_event_description = f"{from_peer.id}->*; {new_txn};"
        new_txn_event = Event(EventType.TXN_BROADCAST, time,
                              time, from_peer.broadcast_txn, (new_txn,), new_txn_event_description)
        time = time + interarrival_time
        simulation.enqueue(new_txn_event)


def export_data(peers):
    '''
    Export data to a file
    '''
    raw_data = {'peers': []}
    peers_data = []
    for peer in peers:
        peers_data.append(peer.__dict__)
    raw_data['peers'] = peers_data
    with open('results.json', 'w') as f:
        json.dump(raw_data, f, indent=4)
    with open('results.yaml', 'w') as f:
        yaml.dump(raw_data, f)
    with open('results.pkl', 'wb') as f:
        pickle.dump(raw_data, f)


if __name__ == "__main__":
    peers = create_network(NUMBER_OF_PEERS)

    log_peers(peers)
    schedule_transactions(peers)

    logger.debug("Simulation started")
    simulation.run()
    logger.debug("Simulation ended")

    export_data(peers)
