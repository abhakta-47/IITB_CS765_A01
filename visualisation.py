import pickle
import pygraphviz as pgv

from utils import create_directory



def visualize(results):
    create_directory('graphs')
    num_peers = len(results['peers'])
    Graph = pgv.AGraph(strict=False, directed=True, rankdir="LR")
    Graph.node_attr["shape"] = "record"
    for peer in results['peers']:
        block_chain = peer['block_chain']
        peer_id = peer['id']
        G = Graph.add_subgraph(
            name=f"cluster_{peer_id}", label=f"Peer {peer_id}")
        G.graph_attr["label"] = f"Peer {peer_id} description: {peer['cpu_net_description']} [ratio:{peer['longest_chain_contribution']}]"

        for block in block_chain['blocks']:
            label = f' {{ id:{block["block_id"]} | miner:{block["miner"]} }} |'
            label = label + \
                f'{{ #tx: {len(block["transactions"])} | ts: {round(block["timestamp"],2)} }}'
            if block['block_id'] != 'gen_blk':
                label = label + \
                    f' | {{ <prev> prev: {block["prev_block"]["hash"][:8]}'
            else:
                label = label + f' | {{ <prev> prev: None'
            label = label + f' | <self> self: {block["self_hash"][:8]} }}'
            if block['self'] in block_chain['longest_chain']:
                G.add_node(peer_id + block['block_id'],
                           color="green", label=label)
            elif block['block_id'] == 'gen_blk':
                G.add_node(peer_id + block['block_id'],
                           color="blue", label=label)
            else:
                G.add_node(peer_id + block['block_id'], label=label)
        for block in block_chain['blocks']:
            if block['prev_block'] == '':
                continue
            prev_block = block['prev_block']
            if block['self'] in block_chain['longest_chain']:
                G.add_edge(
                    peer_id+prev_block['id'], peer_id + block['block_id'],  tailport="self", headport="prev", dir="back", color="green")
            else:
                G.add_edge(peer_id+prev_block['id'], peer_id + block['block_id'],
                           tailport="self", headport="prev", dir="back")
    Graph.draw(f"graphs/graphs.pdf", prog="dot")


if __name__ == '__main__':
    results = ''
    with open('results.pkl', 'rb') as fileobj:
        results = pickle.load(fileobj)

    visualize(results=results)
