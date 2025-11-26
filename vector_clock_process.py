class VectorClock:
    """
    A vector clock implementation for distributed systems.
    Each process maintains its own vector clock to track causality.
    """
    
    def __init__(self, process_id, initial_clock=None):
        """
        Initialize a vector clock for a process.
        
        Args:
            process_id: Unique identifier for this process
            initial_clock: Optional initial state (dict mapping process_id -> counter)
        """
        self.process_id = process_id
        self.clock = initial_clock.copy() if initial_clock else {}
        # Ensure our own process is in the clock
        if self.process_id not in self.clock:
            self.clock[self.process_id] = 0
    
    def increment(self):
        """Increment this process's counter in the vector clock."""
        self.clock[self.process_id] += 1
        return self.clock[self.process_id]
    
    def update(self, received_clock):
        """
        Update this vector clock with a received clock (merge operation).
        This implements the vector clock merge: max(local[i], remote[i]) for all i.
        
        Args:
            received_clock: Another vector clock to merge with
        """
        # Update with max values for all known processes
        all_processes = set(self.clock.keys()) | set(received_clock.keys())
        
        for process_id in all_processes:
            local_val = self.clock.get(process_id, 0)
            remote_val = received_clock.get(process_id, 0)
            self.clock[process_id] = max(local_val, remote_val)
        
        # Increment our own counter after receiving a message
        self.increment()
    
    def compare(self, other_clock):
        """
        Compare this vector clock with another.
        
        Returns:
            -1: this clock happens before other_clock
             0: clocks are concurrent
             1: this clock happens after other_clock
            None: clocks are identical
        """
        if self.clock == other_clock:
            return None
        
        less_than_all = True
        greater_than_all = True
        
        all_processes = set(self.clock.keys()) | set(other_clock.keys())
        
        for process_id in all_processes:
            local_val = self.clock.get(process_id, 0)
            other_val = other_clock.get(process_id, 0)
            
            if local_val < other_val:
                greater_than_all = False
            elif local_val > other_val:
                less_than_all = False
        
        if less_than_all and not greater_than_all:
            return -1  # This happens before
        elif greater_than_all and not less_than_all:
            return 1   # This happens after
        else:
            return 0   # Concurrent
    
    def happens_before(self, other_clock):
        """Check if this clock happens before another clock."""
        return self.compare(other_clock) == -1
    
    def happens_after(self, other_clock):
        """Check if this clock happens after another clock."""
        return self.compare(other_clock) == 1
    
    def is_concurrent(self, other_clock):
        """Check if this clock is concurrent with another clock."""
        return self.compare(other_clock) == 0
    
    def get_clock(self):
        """Get a copy of the current clock state."""
        return self.clock.copy()
    
    def __str__(self):
        """String representation of the vector clock."""
        return f"VectorClock(process={self.process_id}, clock={self.clock})"
    
    def __repr__(self):
        return self.__str__()


class VectorClockProcess:
    """
    A process that uses vector clocks for causal ordering in a distributed system.
    """
    
    def __init__(self, process_id):
        """
        Initialize a process with a vector clock.
        
        Args:
            process_id: Unique identifier for this process
        """
        self.process_id = process_id
        self.vector_clock = VectorClock(process_id)
        self.message_log = []  # Store messages with their vector clocks
    
    def send_message(self, message_content, target_process=None):
        """
        Send a message (simulate sending to another process).
        
        Args:
            message_content: The message to send
            target_process: Optional target process for simulation
            
        Returns:
            Message object with vector clock
        """
        # Increment our clock before sending
        self.vector_clock.increment()
        
        message = {
            'content': message_content,
            'sender': self.process_id,
            'vector_clock': self.vector_clock.get_clock(),
            'target': target_process
        }
        
        print(f"Process {self.process_id} sending message: {message_content}")
        print(f"Current clock: {self.vector_clock.get_clock()}")
        
        return message
    
    def receive_message(self, message):
        """
        Receive a message from another process.
        
        Args:
            message: Message object with vector clock
            
        Returns:
            Boolean indicating if message was accepted (for causal ordering)
        """
        print(f"Process {self.process_id} receiving message: {message['content']}")
        print(f"Received clock: {message['vector_clock']}")
        print(f"Local clock before update: {self.vector_clock.get_clock()}")
        
        # Update our vector clock with the received clock
        self.vector_clock.update(message['vector_clock'])
        
        print(f"Local clock after update: {self.vector_clock.get_clock()}")
        
        # Log the message
        self.message_log.append({
            'message': message,
            'local_clock': self.vector_clock.get_clock().copy(),
            'timestamp': len(self.message_log)
        })
        
        return True
    
    def local_event(self):
        """Perform a local event (increment clock without sending message)."""
        self.vector_clock.increment()
        print(f"Process {self.process_id} local event")
        print(f"Current clock: {self.vector_clock.get_clock()}")
    
    def get_clock_state(self):
        """Get current vector clock state."""
        return self.vector_clock.get_clock()
    
    def compare_with_other(self, other_clock):
        """Compare this process's clock with another clock."""
        return self.vector_clock.compare(other_clock)


# Example usage and demonstration
def demo_vector_clocks():
    """Demonstrate vector clocks in action."""
    print("=== Vector Clock Demonstration ===")
    
    # Create three processes
    process_a = VectorClockProcess("A")
    process_b = VectorClockProcess("B")
    process_c = VectorClockProcess("C")
    
    print("\n--- Initial State ---")
    print(f"Process A: {process_a.get_clock_state()}")
    print(f"Process B: {process_b.get_clock_state()}")
    print(f"Process C: {process_c.get_clock_state()}")
    
    print("\n--- Process A sends message to B ---")
    message1 = process_a.send_message("Hello from A", "B")
    process_b.receive_message(message1)
    
    print("\n--- Process B sends message to C ---")
    message2 = process_b.send_message("Hello from B", "C")
    process_c.receive_message(message2)
    
    print("\n--- Process A sends another message to C ---")
    message3 = process_a.send_message("Second message from A", "C")
    process_c.receive_message(message3)
    
    print("\n--- Process B has local event ---")
    process_b.local_event()
    
    print("\n--- Final State ---")
    print(f"Process A: {process_a.get_clock_state()}")
    print(f"Process B: {process_b.get_clock_state()}")
    print(f"Process C: {process_c.get_clock_state()}")
    
    print("\n--- Clock Comparisons ---")
    print(f"A vs B: {process_a.compare_with_other(process_b.get_clock_state())}")
    print(f"B vs C: {process_b.compare_with_other(process_c.get_clock_state())}")
    print(f"A vs C: {process_a.compare_with_other(process_c.get_clock_state())}")


if __name__ == "__main__":
    demo_vector_clocks()
