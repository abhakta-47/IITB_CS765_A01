import random
from Peer import Peer, Link
import config


def is_connected(peers: list[Peer]):
    """
    Returns True if all peers are connected to each other, False otherwise.
    """
    is_visited = [False] * len(peers)
    cur_peer = peers[0]
    queue = [cur_peer]
    is_visited[0] = True
    while queue:
        cur_peer = queue.pop(0)
        is_visited[cur_peer.id] = True
        for peer in cur_peer.neighbours.keys():
            if not is_visited[peer.id]:
                queue.append(peer)
    return all(is_visited)


def draw_graph(peers):
    """
    Draws a graph of the peers and their connections.
    """
    import networkx as nx
    import matplotlib.pyplot as plt
    G = nx.Graph()
    for peer in peers:
        G.add_node(peer.id)
        for connected_peer in peer.connected_peers:
            G.add_edge(peer.id, connected_peer.id)
    nx.draw(G, with_labels=True)
    plt.show()


def calculate_low_cpu_power(num_peers: int, z1: float):
    deno = (10-9*z1)*num_peers
    neu = 1
    return (neu/deno)


def create_network(n: int):
    peers = [Peer(id=i, is_slow_network=False, is_slow_cpu=False)
             for i in range(n)]

    slow_net_peers = random.sample(peers, int(n * config.Z0))
    for peer in slow_net_peers:
        peer.is_slow_network = True

    slow_cpu_peers = random.sample(peers, int(n * config.Z1))
    low_cpu_power = calculate_low_cpu_power(n, config.Z1)
    high_cpu_power = 10*low_cpu_power
    for peer in slow_cpu_peers:
        peer.is_slow_cpu = True
    for peer in peers:
        if peer.is_slow_cpu:
            peer.cpu_power = low_cpu_power
        else:
            peer.cpu_power = high_cpu_power

    for peer in peers:
        # choose random number of neighbours
        num_neighbours = random.randint(4, 6)
        # num_neighbours = random.randint(2, 3)
        random_neighbours = random.sample(
            peers, num_neighbours)  # choose random neighbours
        for neighbour in random_neighbours:
            if neighbour != peer:  # don't add yourself as a neighbour
                link = Link(peer, neighbour)
                # add neighbour to peer
                peer.connect(peer=neighbour, link=link)
                # add peer to neighbour
                neighbour.connect(peer=peer, link=link)
    return peers
