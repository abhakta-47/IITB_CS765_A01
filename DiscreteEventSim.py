from enum import Enum
from queue import PriorityQueue
from datetime import datetime, timedelta
import logging
import threading

from config import EVENT_QUEUE_TIMEOUT

logger = logging.getLogger(__name__)

class EventType(Enum):
    EVENT_TYPE_1 = "Type 1"
    EVENT_TYPE_2 = "Type 2"
    # Add more event types as needed

class Event:
    def __init__(self, event_type, created_at, delay, action, payload):
        self.type = event_type # type of the event
        self.created_at = created_at # when it is created
        self.delay = delay
        self.actionable_at = self.created_at + delay # when it should be executed
        self.action = action # what to execute
        self.payload = payload # arguments for the action
        self.log_message = "" # log message
    
    def __gt__(self, other):
        return self.actionable_at > other.actionable_at
    def __lt__(self, other):
        return self.actionable_at < other.actionable_at

class Simulation:
    def __init__(self):
        self.clock = 0.0
        self.event_queue = PriorityQueue()
        self.timeout_timer = threading.Timer(EVENT_QUEUE_TIMEOUT, self.dequeue)
    
    def __dequeue_timer(self):
        self.timeout_timer.cancel()
        self.timeout_timer = threading.Timer(EVENT_QUEUE_TIMEOUT, self.dequeue)
        self.timeout_timer.start()

    def enqueue(self, event):
        # Add event to the queue and sort by actionable_at
        logger.debug(f"Enqueuing: {event}")
        self.event_queue.put(event)
        logger.info(f"Enqueued event: {event.type} at {event.actionable_at}")
        logger.info(f"Event payload: {event.payload}\n")
        # start dequeue timer
        self.__dequeue_timer()

    def dequeue(self):
        while not self.event_queue.empty():
            next_event = self.event_queue.get()
            self.clock = next_event.actionable_at
            logger.info(f"Dequeued event: {next_event.type} at {next_event.actionable_at}")
            # Take action on the event (you may need to define appropriate actions)
            next_event.action(*next_event.payload)
            # Update the clock to the time of the dequeued event
            # self.clock = next_event.actionable_at
    
    def __del__(self):
        self.timeout_timer.cancel()

simulation = Simulation()
