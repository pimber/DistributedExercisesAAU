from emulators.Device import Device
from emulators.Medium import Medium
from emulators.MessageStub import MessageStub


class GossipMessage(MessageStub):

    def __init__(self, sender: int, destination: int, secrets):
        super().__init__(sender, destination)
        # we use a set to keep the "secrets" here
        self.secrets = secrets

    def __str__(self):
        return f'{self.source} -> {self.destination} : {self.secrets}'


class Gossip(Device):

    def __init__(self, index: int, number_of_devices: int, medium: Medium):
        super().__init__(index, number_of_devices, medium)
        # for this exercise we use the index as the "secret", but it could have been a new routing-table (for instance)
        # or sharing of all the public keys in a cryptographic system
        self._secrets = set([index])

    def run(self):
        # we will keep sending the secrets until we have all of them
        while len(self._secrets) < self.number_of_devices():
            # we send the secrets to all other devices
            for i in range(0, self.number_of_devices()):
                # we do not send to ourselves
                if i == self.index():
                    continue
                # we send the secrets
                message = GossipMessage(self.index(), i, self._secrets)
                # we send the message via a "medium"
                self.medium().send(message)
                # while sending messages we also try to receive some messages
                while True:
                    ingoing = self.medium().receive()
                    # if the medium returns None, we break the loop
                    if ingoing is None:
                        break
                    self._secrets = self._secrets.union(ingoing.secrets)
        return

    def print_result(self):
        print(f'\tDevice {self.index()} got secrets: {self._secrets}')

class GossipLeftRight(Device):

    def __init__(self, index: int, number_of_devices: int, medium: Medium):
        super().__init__(index, number_of_devices, medium)
        # for this exercise we use the index as the "secret", but it could have been a new routing-table (for instance)
        # or sharing of all the public keys in a cryptographic system
        self._secrets = set([index])

    def run(self):
        # we will keep sending the secrets until we have all of them
        while len(self._secrets) < self.number_of_devices():
            # we can only send the secrets to its neighbors
            left = (self.index() - 1) % self.number_of_devices()
            right = (self.index() + 1) % self.number_of_devices()

            # we send the secrets to the left
            message = GossipMessage(self.index(), left, self._secrets)
            self.medium().send(message)

            # we send the secrets to the right
            message = GossipMessage(self.index(), right, self._secrets)
            self.medium().send(message)

            # while sending messages we also try to receive some messages
            while True:
                ingoing = self.medium().receive()
                # if the medium returns None, we break the loop
                if ingoing is None:
                    break
                self._secrets = self._secrets.union(ingoing.secrets)
        return

    def print_result(self):
        print(f'\tDevice {self.index()} got secrets: {self._secrets}')
