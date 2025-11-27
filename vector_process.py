import threading
import time
from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client


class VectorClock:
    def __init__(self, port, peers=None):
        # changed: accept peers and initialize a vector clock (dict)
        if peers is None:
            peers = []
        self.port = port
        # ensure own port is part of the known nodes
        nodes = set(peers) | {self.port}
        self.clock = {p: 0 for p in nodes}
        self.lock = threading.Lock()

        # XML-RPC server setup
        self.server = SimpleXMLRPCServer(('localhost', self.port), allow_none=True)
        self.server.register_function(self.receive_message, "receive_message")

    def receive_message(self, message):
        # changed: merge incoming vector clocks, then increment own entry
        with self.lock:
            incoming = message.get('clock', {})
            # ensure we include any unknown nodes from incoming message
            for pid, val in incoming.items():
                self.clock[pid] = max(self.clock.get(pid, 0), val)
            # after merge, increment this process's own entry
            old_clock = dict(self.clock)
            self.clock[self.port] = self.clock.get(self.port, 0) + 1
            print(f"Process {self.port}: Received from {message.get('sender_port')} with clock {incoming}, my clock was {old_clock}, clock is now {self.clock}")
        return True

    def _increment_clock(self):
        # changed: increment only this process's vector entry
        while True:
            with self.lock:
                self.clock[self.port] = self.clock.get(self.port, 0) + 1
                print(f"Process {self.port}: Internal event, clock is now {self.clock}")
            time.sleep(1)

    def send_message(self, remote_port):
        # changed: send the entire vector clock
        with xmlrpc.client.ServerProxy(f"http://localhost:{remote_port}/") as remote_server:
            with self.lock:
                message = {
                    'sender_port': self.port,
                    'clock': dict(self.clock)
                }
            try:
                remote_server.receive_message(message)
                print(f"Process {self.port}: Sent to {remote_port} with clock {message['clock']}")
            except ConnectionRefusedError:
                print(f"Process at {remote_port} is dead!!")
            except Exception as e:
                print(f"Error sending to {remote_port}: {e}")


    def start(self):
        # ...existing code...
        server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        increment_thread = threading.Thread(target=self._increment_clock, daemon=True)

        server_thread.start()
        increment_thread.start()

        print(f"Process on port {self.port} started...")


if __name__ == "__main__":
    # changed: demonstrate with known peers so vector has proper entries
    vector_process = VectorClock(8001, peers=[8001, 8002, 8003])
    vector_process.start()

    time.sleep(3)  # Wait for clocks to increment
    print("\n--- Sending message from 8001 to 8002. ---")
    vector_process.send_message(8002)

    time.sleep(10)
    print("\n--- Sending message from 8001 to 8003. ---")
    vector_process.send_message(8003)

    time.sleep(2)
    print("\n--- Sending message from 8001 to 8002. ---")
    vector_process.send_message(8002)

