import random
from message import Message
from node import Node

class Controller(Node):
    def __init__(self, logfile, one_hop, controller_id = 1000001, sdn=True):
        self.nodes = {}
        self.logfile = logfile
        self.inbox = []
        self.outbox = []
        self.controller = self
        self.last_receive = 0
        self.time = -1
        self.id = controller_id
        self.controller_id = controller_id
        self.one_hop = one_hop
        self.type = "Controller"
        self.SDN = sdn
        self.routing_table = {}

    def iterate(self, time):
        for index, node in self.nodes.items():
            node.process_inbox_at_time(time)
            node.process_outbox_at_time(time)
        self.process_inbox_at_time(time)
        self.process_outbox_at_time(time)

    def register(self, node):
        self.nodes[node.id] = node
        node.logfile = self.logfile
        if self.one_hop:
            self.routing_table[node.id] = node.id

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

    def controller_route_message(self, message, target):
        self.outbox.append((target, message))

    def process_message(self, message):
        if message.source != self.id:
            self.logfile.write("Message with ID " + str(message.uid) + " received by node "
                               + str(self.id) + ":\n\t" + str(message.contents) + "\n\t"
                               + "sender: " + str(message.source) + "\n")

        if 'request' in message.contents:
            self.update_routes_for_packet(message.contents['request'])

    def write_network_to_file(self, filename):
        output_file = open(filename, 'w')
        for node in self.nodes.values():
            if node.type == "Controller": continue
            output_file.write(node.type)
            output_file.write(" " + str(node.id) + " ")
            output_file.write(" ".join(",".join([str(x), str(y)]) for x , y in node.neighbors.items()) + "\n")
        output_file.close()

    def get_node(self, nodeid):
        if nodeid == -1:
            return self
        return self.nodes[nodeid]

    def update_routes_for_packet(self, message, sdn=True):

        for source in self.nodes.keys():

            if source == self.id and self.one_hop: continue

            unvisited = {node: None for node in self.nodes.keys()} # None = +inf
            visited = {}
            path = {}
            current_distance = 0
            current = source
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
                if len(candidates) == 0: break
                current, current_distance = sorted(candidates, key = lambda x: x[1])[0]

            if sdn:
                if source != message.destination:
                    path = {message.uid : path[message.destination]}
                else:
                    path = {}

                routing_message = Message({"routing": path}, 0, source, source, self.time, 1, True)
                #for node in self.nodes.keys():
                #    self.outbox.append((node, routing_message))
                self.route_message(routing_message)
            else:
                self.nodes[source].update_routing_table(path)

        flow_msg = Message({'flow':message}, self.id, message.source, message.source, self.time, 1, True)
        if 'init' not in message.contents:
            self.route_message(flow_msg)
