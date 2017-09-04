class Node(object):
    def __init__(self, controller, node_type, uid, neighbors):
        self.position = (0,0,0)
        self.neighbors = dict([tuple([int(a) for a in x.split(",")]) for x in neighbors])
        self.message_queue = []
        self.routing_table = {}
        self.id = int(uid)
        self.controller = controller
        self.type = node_type
        self.logfile = None # register will change this
        controller.register(self)

    def inbox_message(self, message):
        if self.id == message.destination:
            self.process_message(message)
        else:
            self.logfile.write("Message with ID " + str(message.uid) +
                               " ignored by node " + str(self.id) + "\n")

    def process_message(self, message):
        # Insert logic here to actually process the message (it's either a
        # normal packet or a routing table update from the controller)
        self.logfile.write("Message with ID " + str(message.uid) + " received by node "
                           + str(self.id) + ":\n\t" + str(message.contents) + "\n\t"
                           + "sender: " + str(message.source) + "\n")

        if 'routing' in message.contents:
            self.update_routing_table(message.contents['routing'])

    def update_routing_table(self, routing_table):
        for key, value in routing_table.items():
            self.routing_table[key] = value

    def add_neighbor(self, node):
        self.neighbors.append(node)
