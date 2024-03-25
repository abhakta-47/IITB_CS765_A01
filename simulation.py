import random
import json
import pickle
from time import time, strftime
from tqdm import tqdm

from logger import init_logger
from network import is_connected, create_network, draw_graph
from DiscreteEventSim import simulation, Event, EventType
from utils import (
    expon_distribution,
    create_directory,
    change_directory,
    copy_to_directory,
    clear_dir,
)
from visualisation import visualize

import config as CONFIG
from config import NUMBER_OF_PEERS, AVG_TXN_INTERVAL_TIME, NUMBER_OF_TRANSACTIONS

logger = init_logger()
START_TIME = time()
START_TIME = strftime("%Y-%m-%d_%H:%M:%S")


def log_peers(peers):
    """
    print(peers)
    """
    for peer in peers:
        logger.info("peer: %s", peer)
        logger.info("peer id: %s, neighbours: %s", peer.id, peer.connected_peers)
    logger.info(is_connected(peers))


def schedule_transactions(peers):
    """
    Schedule transactions
    """
    time = 0
    while simulation.event_queue.qsize() < NUMBER_OF_TRANSACTIONS:
        # Generate exponential random variable for interarrival time
        interarrival_time = expon_distribution(AVG_TXN_INTERVAL_TIME)
        # logger.debug(f"Interarrival time: {interarrival_time}")
        from_peer = random.choice(peers)
        new_txn_event = Event(
            EventType.TXN_CREATE,
            time,
            time,
            from_peer.generate_random_txn,
            (time,),
            f"{from_peer} create_txn",
        )
        time = time + interarrival_time
        simulation.enqueue(new_txn_event)
    # for i in range(CONFIG.NUMBER_OF_PEERS):
    miner_peer = random.choice(peers)
    time_stamp = time * 2 / 3
    new_block_event = Event(
        EventType.BLOCK_CREATE,
        time_stamp,
        time_stamp,
        miner_peer.block_chain.generate_block,
        (),
        f"{miner_peer} create_block",
    )
    simulation.enqueue(new_block_event)


def export_data(peers):
    """
    Export data to a file
    """
    raw_data = []
    json_data = []
    for peer in peers:
        json_data.append(peer.__dict__)
        raw_data.append(peer)
    json_data = {"peers": json_data}

    if CONFIG.SAVE_RESULTS:
        output_dir = f"output/{START_TIME}"
        create_directory(output_dir)
        copy_to_directory("blockchain_simulation.log", output_dir)
        change_directory(output_dir)
    clear_dir("graphs")
    with open("results.json", "w") as f:
        json.dump(json_data, f, indent=4)
    with open("results.pkl", "wb") as f:
        pickle.dump(json_data, f)
    visualize(json_data)


def setup_progressbars():
    """
    Setup progress bars
    """
    pbar_txns = tqdm(
        desc="Txns: ", total=NUMBER_OF_TRANSACTIONS, position=0, leave=True
    )
    pbar_blocks = tqdm(
        desc="Blks: ",
        total=NUMBER_OF_TRANSACTIONS / CONFIG.BLOCK_TXNS_MAX_THRESHHOLD,
        position=1,
        leave=True,
    )
    return (pbar_txns, pbar_blocks)


blocks_broadcasted = 0


def update_progressbars(pbar_txns, pbar_blocks, event):
    """
    Update progress bars
    """
    global blocks_broadcasted
    if event.type == EventType.TXN_BROADCAST:
        pbar_txns.update(1)
    elif event.type == EventType.BLOCK_BROADCAST:
        blocks_broadcasted += 1
        pbar_blocks.update(1)

    if blocks_broadcasted > CONFIG.MAX_NUM_BLOCKS + 5:
        simulation.stop_sim = True


if __name__ == "__main__":

    peers_network = create_network(NUMBER_OF_PEERS)
    logger.info("Network created")
    print("Network created")
    # draw_graph(peers_network)

    log_peers(peers_network)
    schedule_transactions(peers_network)
    logger.info("Transactions scheduled")
    print("Transactions scheduled")

    logger.info("Simulation started")
    print("Simulation started")
    try:
        (pbar_txns, pbar_blocks) = setup_progressbars()
        simulation.reg_run_hooks(
            lambda event: update_progressbars(pbar_txns, pbar_blocks, event)
        )
        simulation.run()
        logger.info("Simulation ended")
    except KeyboardInterrupt:
        logger.info("Simulation interrupted")
    finally:
        for peer in peers_network:
            peer.flush_blocks()
        pbar_txns.close()
        pbar_blocks.close()
        print("Simulation ended")

        export_data(peers_network)
        logger.info("Data exported")
        print("Data exported")
