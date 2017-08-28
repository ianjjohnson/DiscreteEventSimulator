import random

class Controller(object):
    def __init__(self):
        self.nodes = {}

    def register(self, node):
        self.nodes[node.id] = node

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
