import controller
import node

NEIGHBORS_PER_NODE = 10.0
NUMBER_OF_NODES = 250

controller = controller.Controller()

graph_input = open('graph.dat', 'r')
graph_serialied = graph_input.read().split("\n")
for graph_line in graph_serialied[:-1]:
    items = graph_line.split(" ")
    node.Node(controller, items[0], items[1], items[2:])

# Format:
# TYPE ID NEIGHBORS
# NODE 1 2 3 4
# CONTROLLER 0

# Set up a controller
# Set up all of the nodes
# (there needs to be some sort of neighbor consideration here)



# General process / idea:
# We want to be able to assess different algorithms for actually performing routing
# In the most extreme case, we want to actually update routing tables for each individual packet sent
