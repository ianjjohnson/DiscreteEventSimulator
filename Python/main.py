import controller
import node as nd
import message
import random
import math

lambda_ = 0.2 # Lambda for exponential distribution
NETWORK_ARCHITECTURE = "MESH" # "MESH", "ALBERTO"
MEAN_NEIGHBORS_PER_NODE = 4 # on average, this is 3-4 for mesh
NUMBER_OF_NODES = 50
NUM_ITERATIONS = 2500
MAX_PACKETS_PER_FLOW = 5
UPTIME = 1
MAX_COST = 10
READ_GRAPH = False
SDN = True
SDN_STRATEGY = "ROUTE" # "FLOOD", "BROADCAST", "ROUTE", "GATEWAY"
ONE_HOP_CONTROLLER = False
ASYNC_UPDATES = True
ASYNC_UPDATE_RATE = 100
PRE_APPROVE_ROUTES = True

if(SDN_STRATEGY == "BROADCAST"):
    ONE_HOP_CONTROLLER = False
elif SDN_STRATEGY == "GATEWAY":
    ONE_HOP_CONTROLLER = True

logfile = open('sdn.dat' if SDN else 'net.dat', 'w')
controller = controller.Controller(logfile, ONE_HOP_CONTROLLER, NUMBER_OF_NODES, SDN, SDN_STRATEGY, UPTIME, ASYNC_UPDATES, PRE_APPROVE_ROUTES)

if ONE_HOP_CONTROLLER:
    controller.neighbors = {}
else:
    controller.neighbors = {}
    for i in range(NUMBER_OF_NODES):
        if random.random() < ((MEAN_NEIGHBORS_PER_NODE-2)/NUMBER_OF_NODES):
            controller.neighbors[i] = int(random.random()*MAX_COST)

def generate_network(c):
    nbrs = [[] for _ in range(NUMBER_OF_NODES)]
    for i in range(NUMBER_OF_NODES):
        neighbors = nbrs[i]
        newneighbors = [x for x in range(NUMBER_OF_NODES + (0 if ONE_HOP_CONTROLLER or SDN_STRATEGY in ["FLOOD", "BROADCAST"] else 1))
                    if (x != i and random.random() < ((MEAN_NEIGHBORS_PER_NODE-1-len(neighbors))/NUMBER_OF_NODES))
                    or abs(x-i) == 1]
        for j in newneighbors:
            if(j < NUMBER_OF_NODES):
                nbrs[j].append(i)
        neighbors = neighbors + newneighbors
        neighborstring = "Node " + str(i)
        for n in neighbors:
            neighborstring = neighborstring + " " + str(n) + "," + "1"#str(int(random.random()*MAX_COST) + 1)
        items = neighborstring.split(" ")
        nd.Node(c, items[0], items[1], items[2:], SDN, SDN_STRATEGY, uptime = UPTIME, PRE_APPROVE_ROUTES=PRE_APPROVE_ROUTES)

def generate_network_alberto(c, m = 5):
    num_connections = (m*m-m)/2.0
    for i in range(m):
        neighbors = [x for x in range(m) if x != i]
        neighborstring = "Node " + str(i)
        for n in neighbors:
            neighborstring = neighborstring + " " + str(n) + "," + "1"#str(int(random.random()*MAX_COST) + 1)
        items = neighborstring.split(" ")
        nd.Node(c, items[0], items[1], items[2:], SDN, SDN_STRATEGY, uptime = UPTIME, PRE_APPROVE_ROUTES=PRE_APPROVE_ROUTES)

    for i in range(m, NUMBER_OF_NODES):
        neighbors = []
        while(len(neighbors) == 0):
            for j in range(len(c.nodes)):
                if random.random() <= (len(c.get_node(j).neighbors)/(num_connections) if num_connections != 0 else 1):
                    neighbors.append(j)
        for n in neighbors:
            c.get_node(n).neighbors[i] = 1
            num_connections = num_connections + 2
        neighborstring = "Node " + str(i)
        for n in neighbors:
            neighborstring = neighborstring + " " + str(n) + "," + "1"#str(int(random.random()*MAX_COST) + 1)
        items = neighborstring.split(" ")
        nd.Node(c, items[0], items[1], items[2:], SDN, SDN_STRATEGY, uptime = UPTIME, PRE_APPROVE_ROUTES=PRE_APPROVE_ROUTES)



if(READ_GRAPH):

    graph_input = open('graph.dat', 'r')
    graph_serialied = graph_input.read().split("\n")
    graph_input.close()
    for graph_line in graph_serialied[:-1]:
        items = graph_line.split(" ")
        node.Node(controller, items[0], items[1], items[2:], SDN, SDN_STRATEGY, uptime = UPTIME)

else:
    if NETWORK_ARCHITECTURE == "MESH":
        generate_network(controller)
    elif NETWORK_ARCHITECTURE == "ALBERTO":
        generate_network_alberto(controller)

if SDN_STRATEGY not in ["BROADCAST", "FLOOD"]:
    controller.register(controller)
controller.write_network_to_file("graph.dat")

# Compute Minimum Spanning Tree
if SDN_STRATEGY in ["BROADCAST"]:
    X = [0,1] # The nodes in the MST
    controller.get_node(0).mst_edges.append(1)
    controller.get_node(1).mst_edges.append(0)
    controller_id = controller.get_node(0).controller_id
    index = 0
    while(len(X) != NUMBER_OF_NODES):
        for n in controller.get_node(index).neighbors:
            if n not in X and n < NUMBER_OF_NODES:
                controller.get_node(index).mst_edges.append(n)
                controller.get_node(n).mst_edges.append(index)
                X.append(n)
        index = index + 1

for nodeid, node in controller.nodes.items():
    print(nodeid, node.neighbors, node.mst_edges)

#msg = message.Message({"body":"tests"}, 0, 0, 1, -1, 1)
#controller.get_node(0).send_message(msg, -1)
msg = message.Message({"init":"test"}, 0, 0, 1, -1, 1, False)
controller.update_routes_for_packet(msg, sdn=False)

def init_message(time):
    source = int(random.random()*NUMBER_OF_NODES)
    destination = source
    while destination == source:
        destination = int(random.random()*NUMBER_OF_NODES)
    flow_size = max(1, int(random.random()*MAX_PACKETS_PER_FLOW))
    msg = message.Message({"body":str(nd.msg_num)}, source, source, destination, time, flow_size, False)
    controller.get_node(source).send_message(msg, time)
    nd.msg_num = nd.msg_num + 1

time_since_last_send = 0
for time in range(NUM_ITERATIONS):
    logfile.write("### Beginning Iteration " + str(time) + " ###\n")

    if(ASYNC_UPDATES and time%ASYNC_UPDATE_RATE == 0 and time != 0):
        controller.perform_async_routing_update()

    if random.random() < (1.0 - math.exp(-1.0 * lambda_ * time_since_last_send)):
        init_message(time)
        time_since_last_send = 0

    controller.iterate(time)
    time_since_last_send = time_since_last_send + 1

import numpy as np

print("Number of messages: " + str(nd.msg_num))

print("Wait Time: " + str(len(nd.msg_data['wait_time'])))
# print(msg_data['wait_time'])
print("Mean: " + str(np.mean(nd.msg_data['wait_time'])))
print("Standard Deviation: " + str(np.std(nd.msg_data['wait_time'])))

print("Travel Time: " + str(len(nd.msg_data['travel_time'])))
# print(msg_data['travel_time'])
print("Mean: " + str(np.mean(nd.msg_data['travel_time'])))
print("Standard Deviation: " + str(np.std(nd.msg_data['travel_time'])))

print(nd.msg_data['wait_time'])

if PRE_APPROVE_ROUTES:
    print("Pre approved: " + str(nd.msg_data['pre-approved']))

print("Mean number of neighbors: " + str(np.mean([len(x.neighbors) for x in controller.nodes.values() if x != controller])))

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
