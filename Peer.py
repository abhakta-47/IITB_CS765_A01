class Peer:
    id: int
    is_slow: bool
    connected_peers: list["Peer"]

    def __init__(self, id, is_slow=False):
        self.id = id
        self.is_slow = is_slow
        self.connected_peers = []

    def connect(self, peer):
        self.connected_peers.append(peer)
        
    def disconnect(self, peer):
        self.connected_peers.remove(peer)
    
    def __repr__(self):
        return f"Peer(id={self.id})"
    
    def gen_txn(self):
        pass
        # return Transaction(txn_id, self.id, self.is_slow)
    

def is_connected(peers):
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
        for peer in cur_peer.connected_peers:
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
    
import random
def create_network(n: int):
    peers = [ Peer(i, False) for i in range(n) ]
    for peer in peers:
        num_neighbours = random.randint(4, 6) # choose random number of neighbours
        random_neighbours = random.sample(peers, num_neighbours) # choose random neighbours
        for neighbour in random_neighbours:
            if neighbour != peer: # don't add yourself as a neighbour
                peer.connect(neighbour) # add neighbour to peer
    return peers