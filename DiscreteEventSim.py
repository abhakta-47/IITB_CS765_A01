from enum import Enum
from queue import PriorityQueue
from datetime import datetime, timedelta
import logging
import threading
from time import sleep

from config import EVENT_QUEUE_TIMEOUT
import utils as UITLS

logger = logging.getLogger(__name__)


class EventType(Enum):
    EVENT_TYPE_1 = "Type 1"
    EVENT_TYPE_2 = "Type 2"
    # Add more event types as needed


class Event:
    def __init__(self, event_type, created_at, delay, action, payload, meta_description=""):
        self.id = UITLS.generate_random_id(6)
        self.type = event_type  # type of the event
        self.created_at = created_at  # when it is created
        self.delay = delay
        self.actionable_at = self.created_at + delay  # when it should be executed
        self.action = action  # what to execute
        self.payload = payload  # arguments for the action
        self.log_message = ""  # log message
        # additional information about the event
        self.meta_description = meta_description

    def __gt__(self, other):
        return self.actionable_at > other.actionable_at

    def __lt__(self, other):
        return self.actionable_at < other.actionable_at

    @property
    def actionable_at_formatted(self):
        return format(round(self.actionable_at, 6), ",")

    def __repr__(self) -> str:
        return f"Event({self.id} <{self.type}> @{self.actionable_at_formatted}) {self.meta_description}"


class Simulation:
    def __init__(self):
        self.clock = 0.0
        self.event_queue = PriorityQueue()

    def __enqueue(self, event):
        self.event_queue.put(event)
        logger.debug("Scheduled: %s", event)
        # logger.info(f"Event payload: {event.payload}\n")

    def enqueue(self, event):
        '''
        Enqueue an event to the event queue.
        '''
        self.__enqueue(event)

    def __run(self):
        while not self.event_queue.empty():
            next_event = self.event_queue.get()
            self.clock = next_event.actionable_at
            logger.debug("Running: %s", next_event)
            next_event.action(*next_event.payload)
            # sleep(5)

    def run(self):
        '''
        Start the simulation.
        '''
        # self.is_running = True
        # self.__dequeue_timer()
        self.__run()


simulation = Simulation()
