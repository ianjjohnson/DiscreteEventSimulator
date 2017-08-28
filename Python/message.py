class Message(object):
    def __init__(self, contents, destination):
        self.destination = destination
        self.contents = contents

    def send(self, recipients):
        for recipient in recipients:
            recipient.add_message(self)
