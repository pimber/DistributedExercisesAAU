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

class GossipRing(Device):

    def __init__(self, index: int, number_of_devices: int, medium: Medium):
        super().__init__(index, number_of_devices, medium)
        # for this exercise we use the index as the "secret", but it could have been a new routing-table (for instance)
        # or sharing of all the public keys in a cryptographic system
        self._secrets = set([index])

    def send_secrets_right(self):
            # We want to send a message from our device to girl next to us
            msgFrom = self.index()
            # We send a message to the girl "to our right" (to the first girl if we are the rightmost one)
            msgTo = (self.index() + 1) % self.number_of_devices()

            # Create a Message with all the secrets we know
            msg = GossipMessage(msgFrom, msgTo, self._secrets)

            # and gossip
            self.medium().send(msg)

    def run(self):
            if 0 == self.index():
                self.send_secrets_right()

            while True:
                # Receive a message
                incoming = self.medium().receive()

                if incoming is None:
                    continue
                # When we receive a secret, we remember the gossip
                self._secrets = self._secrets.union(incoming.secrets)

                # This condition leads to the lowest number of messages sent in the ring
                if self.index() != self.number_of_devices() - 2 or len(self._secrets) != self.number_of_devices():
                    # we again send the message like before
                    self.send_secrets_right()

                # and the termination condition
                if len(self._secrets) == self.number_of_devices():
                    return True

    def print_result(self):
        print(f'\tDevice {self.index()} got secrets: {self._secrets}')


# A clique is an undirected graph where every two distinct vertices are adjacent
class GossipClique(Device):

    def __init__(self, index: int, number_of_devices: int, medium: Medium):
        super().__init__(index, number_of_devices, medium)
        # for this exercise we use the index as the "secret", but it could have been a new routing-table (for instance)
        # or sharing of all the public keys in a cryptographic system
        self._secrets = set([index])

    def send_secrets_to(self, destination):
            msgFrom = self.index()

            # Create a Message with all the secrets we know
            msg = GossipMessage(msgFrom, destination, self._secrets)

            # and gossip
            self.medium().send(msg)

    def run(self):
            # Strategy: every node sends the secret to node 0, then 0 broadcasts the secrets vector to all other nodes
            if 0 != self.index():
                self.send_secrets_to(0)

            while True:
                # Receive a message
                incoming = self.medium().receive()

                if incoming is None:
                    continue
                # When we receive a secret, we remember the gossip
                self._secrets = self._secrets.union(incoming.secrets)

                # If node 0 has all secrets, broadcasts, then exits
                if 0 == self.index() and len(self._secrets) == self.number_of_devices():
                    for destination in range(1, self.number_of_devices()):
                        self.send_secrets_to(destination)
                    return True

                # Termination condition for all other nodes
                if len(self._secrets) == self.number_of_devices():
                    return True

    def print_result(self):
        print(f'\tDevice {self.index()} got secrets: {self._secrets}')