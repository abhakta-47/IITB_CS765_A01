import inspect
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
    TXN_CREATE = 'TXN_CREATED'
    TXN_SEND = 'TXN_SENT'
    TXN_RECEIVE = 'TXN_RECEIVED'
    TXN_BROADCAST = 'TXN_BROADCASTED'

    BLOCK_CREATE = 'BLOCK_CREATED'
    BLOCK_SEND = 'BLOCK_SENT'
    BLOCK_RECEIVE = 'BLOCK_RECEIVED'
    BLOCK_BROADCAST = 'BLOCK_BROADCASTED'
    BLOCK_ACCEPTED = 'BLOCK_ACCEPTED'  # BLOCK VALIDATED, ACCEPTED INTO BLOCKCHAIN

    BLOCK_MINE_START = 'BLOCK_MINE_STARTED'
    BLOCK_MINE_FINISH = 'BLOCK_MINE_FINISHED'
    BLOCK_MINE_SUCCESS = 'BLOCK_MINE_SUCCESSFUL'
    BLOCK_MINE_FAIL = 'BLOCK_MINE_FAILED'

    def __str__(self):
        return f"{self.value}"


class Event:
    def __init__(self, event_type: EventType, created_at, delay, action, payload, meta_description=""):
        self.id = UITLS.generate_random_id(6)
        self.type: EventType = event_type  # type of the event
        self.created_at = created_at  # when it is created
        self.delay = delay
        self.actionable_at = self.created_at + delay  # when it should be executed
        self.action = action  # what to execute
        self.payload = payload  # arguments for the action
        self.log_message = ""  # log message
        # additional information about the event
        self.meta_description = meta_description

        self.owner = "nan"
        try:
            self.owner = inspect.currentframe().f_back.f_locals['self']
        except Exception:
            try:
                self.owner = inspect.currentframe().f_back.f_locals['module']
            except Exception:
                pass

    def __gt__(self, other):
        return self.actionable_at > other.actionable_at

    def __lt__(self, other):
        return self.actionable_at < other.actionable_at

    @property
    def created_at_formatted(self):
        return format(round(self.created_at, 6), ",")

    @property
    def actionable_at_formatted(self):
        return format(round(self.actionable_at, 6), ",")

    def __repr__(self) -> str:
        return f"📆({self.id} 🔀:{self.type} 👷:{self.owner} ⏰️:{self.created_at_formatted}-{self.actionable_at_formatted} 📦:{self.payload}) 📝:\"{self.meta_description}\""


class Simulation:
    def __init__(self):
        self.clock = 0.0
        self.event_queue = PriorityQueue()

    def __enqueue(self, event):
        self.event_queue.put(event)
        # logger.debug("Scheduled: %s", event)
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
