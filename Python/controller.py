import random
from message import Message

class Controller(object):
    def __init__(self, logfile):
        self.nodes = {}
        self.logfile = logfile
        self.message_id_counter = 0

    def register(self, node):
        self.nodes[node.id] = node
        node.logfile = self.logfile

    def assign_neighbors(self, mean_neighbors_per_node):
        num_nodes = len(self.nodes)
        for i in range(num_nodes):
            for _ in range(int(mean_neighbors_per_node / 2)):
                j = i
                # Prevent self-looping and duplicate connections
                while(j == i or j in self.nodes[i].neighbors):
                    j = int(random.random() * num_nodes)
                self.nodes[i].add_neighbor(self.nodes[j])
                self.nodes[j].add_neighbor(self.nodes[i])

    def send_message_to_every_node(self, message):
        for node in self.nodes.values():
            node.inbox_message(message)

    def write_network_to_file(self, filename):
        output_file = open(filename, 'w')
        for node in self.nodes.values():
            output_file.write(node.type)
            output_file.write(" " + str(node.id) + " ")
            output_file.write(" ".join(",".join([str(x), str(y)]) for x , y in node.neighbors.items()) + "\n")
        output_file.close()

    def update_routes_for_packet(self, message):

        for current in self.nodes.keys():

            unvisited = {node: None for node in self.nodes.keys()} # None = +inf
            visited = {}
            path = {}
            current_distance = 0
            unvisited[current] = current_distance

            while True:
                for neighbor, distance in self.nodes[current].neighbors.items():
                    if neighbor not in unvisited: continue
                    new_distance = current_distance + distance
                    if unvisited[neighbor] is None or unvisited[neighbor] > new_distance:
                        unvisited[neighbor] = new_distance
                        path[neighbor] = current
                visited[current] = current_distance
                del unvisited[current]
                if not unvisited: break
                candidates = [node for node in unvisited.items() if node[1]]
                current, current_distance = sorted(candidates, key = lambda x: x[1])[0]

            routing_message = Message(self.message_id_counter, {"routing": path}, 0, current)
            for node in self.nodes.keys():
                self.nodes[node].inbox_message(routing_message)
