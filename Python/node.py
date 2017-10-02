from message import Message
import copy

class Node(object):
    def __init__(self, controller, node_type, uid, neighbors, SDN):
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
        controller.register(self)

    def inbox_message(self, message, send_time):
        if self.last_receive == self.time:
            return False
        message.last_send = send_time
        self.inbox.append(message)
        self.last_receive = self.time
        return True

    def process_inbox_at_time(self, time):
        self.time = time
        for index, message in enumerate(self.inbox):
            if message.last_send >= time:
                continue
            del self.inbox[index]
            if self.id == message.recipient or message.is_sdn_control:
                self.process_message(message)
            else:
                self.logfile.write("Message with ID " + str(message.uid) +
                                   " ignored by node " + str(self.id) + "\n")

    def process_outbox_at_time(self, time):
        index = 0
        for index in range(len(self.outbox)):
            next_hop, message = self.outbox[index]
            if self.controller.get_node(next_hop).inbox_message(message, self.time):
                self.logfile.write("Message with ID " + str(message.uid) +
                                   " sent by node " + str(self.id) + " to node "
                                   + str(next_hop) + ".\n")
                if self.id != self.controller_id and message.uid in self.outbox_timing:
                    delta = time - self.outbox_timing[message.uid]
                    self.logfile.write("Wait time: " + str(delta) + "\n")
                    message.msg_data['wait_time'].append(delta)
                    if not message.is_sdn_control:
                        message.msg_data['arrival'][message.uid] = time
                    del self.outbox_timing[message.uid]
                del self.outbox[index]
                break

    def process_message(self, message):
        self.logfile.write("Message with ID " + str(message.uid) + " received by node "
                           + str(self.id) + ":\n\t" + str(message.contents) + "\n\t"
                           + "sender: " + str(message.source) + "\n")

        if 'flow' in message.contents:
            self.add_flow_to_outbox(message.contents['flow'])
        if 'routing' in message.contents and message.destination == self.id:
            self.update_routing_table(message.contents['routing'])
        if not self.route_message(message):
            self.inbox.append(message)

    def add_flow_to_outbox(self, message):
        flowsize = message.flowsize
        message.flowsize = 1
        for _ in range(flowsize):
            self.route_message(copy.copy(message))

    def route_message(self, message):
        key = message.uid if self.SDN else message.destination
        if message.is_sdn_control:
            key = message.destination
        if key not in self.routing_table:
            if message.destination == self.id:
                self.logfile.write("Message with ID " + str(message.uid) + " arrived at destination node " + str(self.id) + ".\n")
                if not message.is_sdn_control and message.uid in message.msg_data['arrival']:
                    message.msg_data['travel_time'].append(self.time - message.msg_data['arrival'][message.uid])
                    del message.msg_data['arrival'][message.uid]
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
            msg = Message({'request':message}, self.id, self.controller_id, self.controller_id, time, 1, True)
            self.route_message(msg)
        else:
            self.add_flow_to_outbox(message)
