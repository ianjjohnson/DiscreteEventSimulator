class Message(object):
    def __init__(self, contents, source, recipient, destination, last_send, flowsize, is_sdn_control, msg_data = {}, broadcast_sender = -1):
        self.source = source
        self.recipient = recipient
        self.destination = destination
        self.contents = contents
        self.type = "Message"
        self.last_send = last_send
        self.uid = hash(str([self.source, self.destination, self.contents, self.type]))
        self.flowsize = flowsize
        self.is_sdn_control = is_sdn_control
        self.creation_time = last_send
        self.msg_data = msg_data
        self.broadcast_sender = broadcast_sender

    def send(self, recipients):
        for recipient in recipients:
            recipient.add_message(self)
