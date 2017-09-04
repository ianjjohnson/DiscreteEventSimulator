class Message(object):
    def __init__(self, uid, contents, source, destination):
        self.uid = uid
        self.source = source
        self.destination = destination
        self.contents = contents
        self.type = "Message"

    def send(self, recipients):
        for recipient in recipients:
            recipient.add_message(self)
