import controller
import node
import message
import random

MEAN_NEIGHBORS_PER_NODE = 10.0
NUMBER_OF_NODES = 5
NUM_ITERATIONS = 1000
NUM_FLOWS = 50
MAX_PACKETS_PER_FLOW = 5
MAX_COST = 10
READ_GRAPH = False
SDN = True

logfile = open('log.dat', 'w')
controller = controller.Controller(logfile)

def generate_network(c):
    for i in range(NUMBER_OF_NODES):
        neighbors = [x for x in range(NUMBER_OF_NODES)
                    if (x != i and random.random() < ((MEAN_NEIGHBORS_PER_NODE-2)/NUMBER_OF_NODES))
                    or abs(x-i) == 1]
        neighborstring = "Node " + str(i)
        for n in neighbors:
            neighborstring = neighborstring + " " + str(n) + "," + str(int(random.random()*MAX_COST))
        items = neighborstring.split(" ")
        node.Node(c, items[0], items[1], items[2:], SDN)


if(READ_GRAPH):

    graph_input = open('graph.dat', 'r')
    graph_serialied = graph_input.read().split("\n")
    graph_input.close()
    for graph_line in graph_serialied[:-1]:
        items = graph_line.split(" ")
        node.Node(controller, items[0], items[1], items[2:], SDN)

else:

    generate_network(controller)

controller.write_network_to_file("network.dat")

if not SDN:
    msg = message.Message({"body":"tests"}, 0, 0, 1, -1, 1)
    controller.update_routes_for_packet(msg, sdn=SDN)

for nodeid, node in controller.nodes.items():
    print(nodeid, node.routing_table)

#msg = message.Message({"body":"tests"}, 0, 0, 1, -1, 1)
#controller.get_node(0).send_message(msg, -1)

msg_num = 0
for time in range(NUM_ITERATIONS):
    logfile.write("### Beginning Iteration " + str(time) + " ###\n")
    controller.iterate(time)

    source = int(random.random()*NUMBER_OF_NODES)
    destination = source
    while destination == source:
        destination = int(random.random()*NUMBER_OF_NODES)
    flow_size = int(random.random()*MAX_PACKETS_PER_FLOW)
    msg = message.Message({"body":str(msg_num)}, source, source, destination, time, flow_size)
    controller.get_node(source).send_message(msg, time)

# Format:
# TYPE ID NEIGHBORS (neighbor,distance neighbor,distance)
# NODE 1 2 3 4
# CONTROLLER 0

# Set up a controller
# Set up all of the nodes
# (there needs to be some sort of neighbor consideration here)



# General process / idea:
# We want to be able to assess different algorithms for actually performing routing
# In the most extreme case, we want to actually update routing tables for each individual packet sent
