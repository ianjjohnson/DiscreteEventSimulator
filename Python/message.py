class Message(object):
    def __init__(self, contents, source, recipient, destination, last_send, flowsize):
        self.source = source
        self.recipient = recipient
        self.destination = destination
        self.contents = contents
        self.type = "Message"
        self.last_send = last_send
        self.uid = hash(str([self.source, self.destination, self.contents, self.type]))
        self.flowsize = flowsize

    def send(self, recipients):
        for recipient in recipients:
            recipient.add_message(self)
