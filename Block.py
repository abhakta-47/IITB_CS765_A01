from typing import Any
import random
from copy import deepcopy

from Transaction import Transaction

from DiscreteEventSim import simulation, Event


class Block:
    block_id: int
    prev_block: "Block"
    transactions: list[Transaction]
    timestamp: float

    @property
    def size(self) -> int:
        '''
        size in kB
        '''
        return len(self.transactions)+1
