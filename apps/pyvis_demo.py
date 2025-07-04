from pyvis.network import Network
import json

with open('data/entities_relationships.json', 'r') as file:
    data = json.load(file)

net = Network(notebook=False, directed=True)

for node in data[0]['nodes']:
    net.add_node(node['id'], label=node['label'])

for edge in data[0]['edges']:
    net.add_edge(edge['from'], edge['to'], title=edge['label'])

net.write_html('graph.html')

