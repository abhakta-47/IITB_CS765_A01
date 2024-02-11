import random
import json
import pickle
from time import time, strftime

from logger import init_logger
from network import is_connected, create_network
from DiscreteEventSim import simulation, Event, EventType
from utils import expon_distribution, create_directory, change_directory, copy_to_directory

from config import NUMBER_OF_PEERS, AVG_TXN_INTERVAL_TIME, NUMBER_OF_TRANSACTIONS

logger = init_logger()
START_TIME = time()
START_TIME = strftime("%Y-%m-%d_%H:%M:%S")


def log_peers(peers):
    '''
    print(peers)
    '''
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
        interarrival_time = expon_distribution(AVG_TXN_INTERVAL_TIME)
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

    output_dir = f"output/{START_TIME}"
    create_directory(output_dir)
    copy_to_directory('blockchain_simulation.log', output_dir)
    change_directory(output_dir)

    with open('results.json', 'w') as f:
        json.dump(raw_data, f, indent=4)
    with open('results.pkl', 'wb') as f:
        pickle.dump(raw_data, f)


if __name__ == "__main__":
    peers_network = create_network(NUMBER_OF_PEERS)
    logger.debug("Network created")
    print("Network created")

    log_peers(peers_network)
    schedule_transactions(peers_network)
    logger.debug("Transactions scheduled")
    print("Transactions scheduled")

    logger.debug("Simulation started")
    print("Simulation started")
    try:
        simulation.run()
        logger.debug("Simulation ended")
        print("Simulation ended")
    except KeyboardInterrupt:
        logger.debug("Simulation interrupted")
        print("Simulation interrupted")
    finally:
        export_data(peers_network)
        logger.debug("Data exported")
        print("Data exported")
