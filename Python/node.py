class Node(object):
    def __init__(self, controller, node_type, uid, neighbors):
        self.position = (0,0,0)
        self.neighbors = [int(x) for x in neighbors]
        self.message_queue = []
        self.routing_table = {}
        self.id = int(uid)
        self.controller = controller
        self.type = node_type

        controller.register(self)

    def inbox_message(self, message):
        if self.id == message.destination:
            self.process_message(message)

    def process_message(self, message):
        # Insert logic here to actually process the message (it's either a
        # normal packet or a routing table update from the controller)
        pass

    def add_neighbor(self, node):
        self.neighbors.append(node)
