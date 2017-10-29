from message import Message
import random
import copy

msg_num = 0
msg_data = {'wait_time' : [], 'arrival': {}, 'travel_time': [], 'overhead_nodes': 0, 'pre-approved': 0}

class Node(object):
    def __init__(self, controller, node_type, uid, neighbors, SDN, SDN_STRATEGY, uptime = 1.0, PRE_APPROVE_ROUTES = False):
        self.position = (0,0,0)
        self.neighbors = dict([tuple([int(a) for a in x.split(",")]) for x in neighbors])
        self.inbox = []
        self.outbox = []
        self.outbox_timing = {}
        self.routing_table = {}
        if controller.one_hop:
            self.routing_table[controller.id] = controller.id
        self.id = int(uid)
        self.controller = controller
        self.controller_id = controller.id
        self.type = node_type
        self.logfile = None # register will change this
        self.last_receive = -1
        self.time = 0
        self.SDN = SDN
        self.floodmap = {}
        self.mst_edges = []
        self.sdn_strategy = SDN_STRATEGY
        self.uptime = uptime
        self.awake = True
        self.pre_approve_routes = PRE_APPROVE_ROUTES
        self.pending_new_route = {}
        controller.register(self)

    def inbox_message(self, message, send_time):
        if self.last_receive == self.time:
            return False
        message.last_send = send_time
        if self.awake:
            self.inbox.append(message)
        self.last_receive = self.time
        return True

    def process_inbox_at_time(self, time):
        self.awake = self.sdn_strategy != "FLOOD" or random.random() < self.uptime
        self.time = time
        for index, message in enumerate(self.inbox):
            if message.last_send >= time:
                continue
            del self.inbox[index]
            if self.id == message.recipient or message.is_sdn_control or self.sdn_strategy in ["BROADCAST", "FLOOD", "GATEWAY"]:
                self.process_message(message)
            else:
                self.logfile.write("Message with ID " + str(message.uid) +
                                   " ignored by node " + str(self.id) + "\n")

    def process_outbox_at_time(self, time):
        for index in range(len(self.outbox)):
            next_hop, message = self.outbox[index]
            if self.controller.get_node(next_hop).inbox_message(message, self.time):
                self.logfile.write("Message with ID " + str(message.uid) +
                                   " sent by node " + str(self.id) + " to node "
                                   + str(next_hop) + ".\n")
                if self.id != self.controller_id and message.uid in self.outbox_timing:
                    delta = time - self.outbox_timing[message.uid]
                    self.logfile.write("Wait time: " + str(delta) + "\n")
                    msg_data['wait_time'].append(delta)
                    if not message.is_sdn_control:
                        msg_data['arrival'][message.uid] = time
                    del self.outbox_timing[message.uid]
                del self.outbox[index]
                return

    def process_message(self, message):
        self.logfile.write("Message with ID " + str(message.uid) + " received by node "
                           + str(self.id) + ":\n\t" + str(message.contents) + "\n\t"
                           + "sender: " + str(message.source) + "\n")

        if self.SDN and self.sdn_strategy in ["BROADCAST", "FLOOD"]:
            self.broadcast_message(message)
            return

        if 'flow' in message.contents:
            if not self.pre_approve_routes:
                self.add_flow_to_outbox(message.contents['flow'])
        if 'routing' in message.contents and message.destination == self.id:
            self.update_routing_table(message.contents['routing'])
            if self.pre_approve_routes:
                for m_id in message.contents['routing'].keys():
                    if m_id in self.pending_new_route:
                        del self.pending_new_route[m_id]
        if not self.route_message(message):
            self.inbox.append(message)

    def add_flow_to_outbox(self, message):
        flowsize = message.flowsize
        message.flowsize = 1
        for i in range(flowsize):
            if self.SDN:
                if self.sdn_strategy in ["BROADCAST", "FLOOD"]:
                    tmp = copy.copy(message)
                    tmp.flow_num = i
                    self.broadcast_message(tmp)
                elif self.sdn_strategy == "GATEWAY":
                    self.outbox.append((self.controller_id, message))
                elif self.sdn_strategy == "ROUTE":
                    self.inbox.append(copy.copy(message))
            else:
                self.route_message(copy.copy(message))

    def broadcast_message(self, message):
        if self.id == message.destination:
            self.arrive(message)
            return
        if (message.uid, message.flow_num) in self.floodmap:
            return
        sender = message.broadcast_sender
        message.broadcast_sender = self.id
        for n in (self.mst_edges if self.sdn_strategy in ["BROADCAST"] else self.neighbors):
            if n != sender and n != self.id:
                self.outbox.append((n, message))
        self.floodmap[(message.uid, message.flow_num)] = 1

    def arrive(self, message):
        self.logfile.write("Message with ID " + str(message.uid) + " arrived at destination node " + str(self.id) + ".\n")
        if not message.is_sdn_control and message.uid in msg_data['arrival']:
            msg_data['travel_time'].append(self.time - msg_data['arrival'][message.uid])
            del msg_data['arrival'][message.uid]

    def route_message(self, message):
        key = message.uid if self.SDN else message.destination
        if message.is_sdn_control:
            key = message.destination
        if key not in self.routing_table:
            if message.destination == self.id:
                self.arrive(message)
            else:
                self.logfile.write("ERROR: No routing information for key: " + str(key)
                               + " at node " + str(self.id) + ". Returning to inbox. This is a transient error.\n")
                return False
            return True
        next_hop = self.routing_table[key]
        if (next_hop == self.id):
            next_hop = message.destination
        message.recipient = next_hop
        self.outbox.append((next_hop, message))
        return True

    def update_routing_table(self, routing_table):
        for key, value in routing_table.items():
            self.routing_table[key] = value

    def add_neighbor(self, node):
        self.neighbors.append(node)

    def send_message(self, message, time):
        self.outbox_timing[message.uid] = time
        if self.SDN:
            if self.sdn_strategy == "ROUTE":
                msg = Message({'request':message}, self.id, self.controller_id, self.controller_id, time, 1, True)
                if self.pre_approve_routes:
                    self.outbox_timing[message.uid] = self.outbox_timing[message.uid] + 1 # correct for fact that we add it to inbox here
                    self.add_flow_to_outbox(message)
                    if (self.id, message.destination) not in self.pending_new_route.values():
                        self.controller.update_routes_for_packet(message, real_arrival = False)
                        msg_data['pre-approved'] = msg_data['pre-approved'] + 1
                    self.pending_new_route[message.uid] = (self.id, message.destination)
                self.route_message(msg)
            elif self.sdn_strategy in ["BROADCAST", "FLOOD", "GATEWAY"]:
                self.add_flow_to_outbox(message)
        else:
            self.add_flow_to_outbox(message)
