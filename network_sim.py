from Peer import Peer, is_connected, draw_graph, create_network

n = 20 # number of peers

while True:
    peers = create_network(n)
    if is_connected(peers):
        break

# print(peers)
for peer in peers:
    print(peer.id, peer.connected_peers)
print(is_connected(peers)) # should be False
draw_graph(peers)