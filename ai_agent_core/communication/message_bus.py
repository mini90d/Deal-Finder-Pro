# This module will handle communication between different components of the agent.
# It can also be used for inter-agent communication if applicable.

class MessageBus:
    def __init__(self):
        # Initialize message bus settings (e.g., connection to a message broker)
        self.subscribers = {} # topic -> list of callbacks
        pass

    def publish(self, topic, message):
        # Placeholder for publishing a message to a topic
        print(f"Publishing to topic '{topic}': {message}")
        if topic in self.subscribers:
            for callback in self.subscribers[topic]:
                try:
                    callback(message)
                except Exception as e:
                    print(f"Error calling subscriber for topic {topic}: {e}")

    def subscribe(self, topic, callback):
        # Placeholder for subscribing to a topic
        print(f"Subscribing to topic '{topic}'")
        if topic not in self.subscribers:
            self.subscribers[topic] = []
        if callback not in self.subscribers[topic]:
            self.subscribers[topic].append(callback)
        else:
            print(f"Callback already subscribed to topic '{topic}'")

    def unsubscribe(self, topic, callback):
        # Placeholder for unsubscribing from a topic
        print(f"Unsubscribing from topic '{topic}'")
        if topic in self.subscribers and callback in self.subscribers[topic]:
            self.subscribers[topic].remove(callback)
            if not self.subscribers[topic]: # Remove topic if no subscribers left
                del self.subscribers[topic]
        else:
            print(f"Callback not found or topic '{topic}' does not exist.")
