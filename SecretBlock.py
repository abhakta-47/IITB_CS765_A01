from typing import Any
import random
from copy import deepcopy
from functools import reduce
from Transaction import Transaction, CoinBaseTransaction
import logging

from DiscreteEventSim import simulation, Event, EventType
from Block import GENESIS_BLOCK, Block
import config
from utils import expon_distribution, generate_random_id

logger = logging.getLogger(__name__)


class PrivateBlockChain:
    def __init__(
        self,
        cpu_power: float,
        broadcast_block_function: Any,
        peers: list[Any],
        owner_peer: Any,
    ):
        self.__blocks: list[Block] = []
        self.__peer_id: Any = owner_peer
        self.__new_transactions: list[Transaction] = []
        self.__block_arrival_time: dict[Block, float] = {}
        self.__broadcast_block: Any = broadcast_block_function
        self.__mining_new_blocks: list[Block] = []

        self.__longest_chain_length: int = 0
        self.__longest_chain_leaf: Block = None

        self.__secret_chain_length: int = 0
        self.__secret_chain_leaf: Block = None

        self.__current_parent_block: Block = None

        self.__branch_lengths: dict[Block, int] = {}
        self.__branch_balances: dict[Block, dict[Any, int]] = {}
        self.__branch_transactions: dict[Block, list[Transaction]] = {}
        self.__missing_parent_blocks: list[Block] = []

        self.avg_interval_time = config.AVG_BLOCK_MINING_TIME
        self.cpu_power: float = cpu_power

        self.secret_blocks: list[Block] = []
        self.lead: int = 0

        self.__init_genesis_block(peers)
        self.__current_parent_block = self.__longest_chain_leaf
        self.__generate_block()

    @property
    def __dict__(self) -> dict:
        blocks = list(map(lambda x: x.__dict__, self.__blocks))
        blocks = sorted(blocks, key=lambda x: x["block_id"])
        block_arrival_times = list(
            map(
                lambda x: {x.__repr__(): self.__block_arrival_time[x]},
                self.__block_arrival_time,
            )
        )
        block_arrival_times = sorted(
            block_arrival_times, key=lambda x: list(x.values())[0]
        )
        longest_chain = self.__get_longest_chain()
        longest_chain = list(map(lambda x: x.__repr__(), longest_chain))
        return {
            "blocks": blocks,
            "block_arrival_time": block_arrival_times,
            "longest_chain_length": self.__longest_chain_length,
            "longest_chain_leaf": self.__longest_chain_leaf.__repr__(),
            "avg_interval_time": self.avg_interval_time,
            "cpu_power": self.cpu_power,
            "longest_chain": longest_chain,
        }

    @property
    def peer_id(self) -> Any:
        return self.__peer_id

    def __repr__(self) -> str:
        return f"BlockChain(👥:{self.__peer_id})"

    def __init_genesis_block(self, peers: list[Any]):
        genesis_block = GENESIS_BLOCK
        self.__blocks.append(genesis_block)
        self.__longest_chain_length = 1
        self.__longest_chain_leaf = genesis_block
        self.__branch_lengths[genesis_block] = 1
        self.__branch_balances[genesis_block] = {}
        self.__branch_transactions[genesis_block] = []
        for peer in peers:
            self.__branch_balances[genesis_block].update({peer: config.INITIAL_COINS})

    def __validate_block(self, block: Block) -> bool:
        """
        1. validate all transactions
        2. transactions are not repeated
        """
        prev_block = block.prev_block
        if prev_block not in self.__blocks:
            logger.info(
                "%s block_dropped %s previous block missing !!", self.peer_id, block
            )
            if block not in self.__missing_parent_blocks:
                self.__missing_parent_blocks.append(block)
            return False
        if block in self.__blocks:
            logger.info(
                "%s block_dropped %s block already in blockchain !!",
                self.peer_id,
                block,
            )
            return False
        for transaction in block.transactions:
            if not self.__validate_transaction(transaction, prev_block):
                logger.info(
                    "%s block_dropped %s invalid transaction !!", self.peer_id, block
                )
                return False
            if transaction in self.__branch_transactions[prev_block]:
                logger.info(
                    "%s block_dropped %s %s transaction already in blockchain!!",
                    self.peer_id,
                    block,
                    transaction,
                )
                return False

        # logger.debug(f"Block {block} is valid")
        return True

    def __validate_transaction(
        self, transaction: Transaction, prev_block: Block
    ) -> bool:
        """
        1. no balance of any peer shouldn't go negative
        """
        balances_upto_block = self.__branch_balances[prev_block]
        if (
            transaction.from_id
            and balances_upto_block[transaction.from_id] < transaction.amount
        ):
            # logger.debug(f"Transaction {transaction} is invalid")
            return False

        # logger.debug(f"Transaction {transaction} is valid")
        return True

    def __update_chain_length(self, block: Block):
        prev_block = block.prev_block
        chain_len_upto_block = self.__branch_lengths[prev_block] + 1
        self.__branch_lengths[block] = chain_len_upto_block
        # self.__branch_lengths.pop(prev_block)
        # logger.debug(f"Chain length upto block {block} is {chain_len_upto_block}")

    def __update_balances(self, block: Block):
        prev_block = block.prev_block
        balances_upto_block = self.__branch_balances[prev_block].copy()
        for transaction in block.transactions:
            if transaction.from_id:
                balances_upto_block[transaction.from_id] -= transaction.amount
            balances_upto_block[transaction.to_id] += transaction.amount
        self.__branch_balances[block] = balances_upto_block
        # self.__branch_balances.pop(prev_block)
        # logger.debug(f"Balances upto block {block} are {balances_upto_block}")

    def __update_avg_interval_time(self, block: Block):
        return
        # prev_block = block.prev_block
        # num_blocks = len(self.__blocks)
        # if num_blocks == 1:
        #     return
        # interval_time = block.timestamp - prev_block.timestamp
        # self.avg_interval_time = (
        #     self.avg_interval_time * (num_blocks-1) + interval_time) / num_blocks
        # logger.debug("Avg interval updated %s", self.avg_interval_time)

    def __update_branch_transactions(self, block: Block):
        prev_block = block.prev_block
        prev_branch_txns = (self.__branch_transactions[prev_block]).copy()
        for transaction in block.transactions:
            prev_branch_txns.append(transaction)
        self.__branch_transactions[block] = prev_branch_txns

    def __update_block_arrival_time(self, block: Block):
        self.__block_arrival_time[block] = simulation.clock

    def __add_block(self, block: Block) -> bool:
        """
        Add a block to the chain
        """
        for transaction in block.transactions:
            # if transaction in self.__new_transactions:
            if isinstance(transaction, CoinBaseTransaction):
                continue
            if transaction in self.__new_transactions:
                self.__new_transactions.remove(transaction)

        self.__blocks.append(block)
        self.__update_chain_length(block)
        self.__update_balances(block)
        self.__update_block_arrival_time(block)
        self.__update_avg_interval_time(block)
        self.__update_branch_transactions(block)

    def __validate_saved_blocks(self):
        remove_blocks = []
        for block in self.__missing_parent_blocks:
            if self.__validate_block(block):
                remove_blocks.append(block)
                self.__add_block(block)
        for block in remove_blocks:
            self.__missing_parent_blocks.remove(block)

    def add_block(self, block: Block) -> bool:
        """
        validate and then add a block to the chain
        """
        if not self.__validate_block(block):
            return False

        self.__add_block(block)
        self.__validate_saved_blocks()

        if block.miner == self.__peer_id:
            self.__secret_chain_leaf = block
            self.__secret_chain_length = self.__branch_lengths[block]
            self.__update_lead(1)
        elif self.__longest_chain_length < self.__branch_lengths[block]:
            self.__public_chain_leaf = block
            self.__longest_chain_length = self.__branch_lengths[block]
            # logger.debug(
            #     "%s <longest_chain> %s %s generating new block !!",
            #     self.__peer_id,
            #     str(self.__longest_chain_length),
            #     str(chain_len_upto_block),
            # )
            # self.__longest_chain_length = chain_len_upto_block
            # self.__longest_chain_leaf = block
            # if block.miner != self.__peer_id:
            self.__update_lead(-1)
            # else:
            # self.__update_lead(1)

    def add_transaction(self, transaction: Transaction) -> bool:
        """
        Add a transaction to the chain
        """
        # if transaction in self.__branch_transactions:
        # return
        self.__new_transactions.append(transaction)
        if transaction.from_id == self.__peer_id:
            return
        # if (
        #     len(self.__mining_new_blocks) == 0
        #     and len(self.__new_transactions) >= config.BLOCK_TXNS_MAX_THRESHHOLD
        # ):
        #     self.__generate_block()

    def __mine_block_start(self, block: Block):
        delay = expon_distribution(self.avg_interval_time / self.cpu_power)

        new_event = Event(
            EventType.BLOCK_MINE_FINISH,
            simulation.clock,
            delay,
            self.__mine_block_end,
            (block,),
            f"mining block finished {block}",
        )
        simulation.enqueue(new_event)

    def __mine_block_end(self, block: Block):
        """
        Broadcast a block to all connected peers.
        """
        self.__mining_new_blocks.remove(block)
        if block.prev_block == self.__current_parent_block and self.__validate_block(
            block
        ):
            logger.info(
                "%s <%s> %s", self.__peer_id, EventType.BLOCK_MINE_SUCCESS, block
            )
            block.transactions.append(
                CoinBaseTransaction(self.__peer_id, block.timestamp)
            )
            self.secret_blocks.append(block)
            self.add_block(block)
            new_event = Event(
                EventType.BLOCK_MINE_SUCCESS,
                simulation.clock,
                0,
                self.__mine_success_handler,
                (block,),
                f"{self.__peer_id}->* broadcast {block}",
            )
            simulation.enqueue(new_event)
            # if len(self.__blocks) > config.MAX_NUM_BLOCKS:
            # simulation.stop_sim = True
        else:
            # no longer longest chain
            logger.info("%s <%s> %s", self.__peer_id, EventType.BLOCK_MINE_FAIL, block)
            # self.generate_block()
        # logger.info("restarting block minining")
        self.__generate_block()

    def __mine_success_handler(self, block: Block):
        new_event = Event(
            EventType.BLOCK_BROADCAST,
            simulation.clock,
            0,
            self.__broadcast_block,
            (block,),
            f"{self.__peer_id}->* broadcast {block}",
        )
        simulation.enqueue(new_event)

    def __generate_block(self) -> Block:
        """
        Generate a new block
        """
        sorted(self.__new_transactions, key=lambda x: x.timestamp)
        valid_transactions_for_longest_chain = []
        # if len(self.secret_blocks):
        # parent_block = self.secret_blocks[-1]
        # else:

        parent_block = self.__current_parent_block
        balances_upto_block = self.__branch_balances[parent_block].copy()
        for transaction in self.__new_transactions:
            if balances_upto_block[transaction.from_id] < transaction.amount:
                continue
            balances_upto_block[transaction.from_id] -= transaction.amount
            balances_upto_block[transaction.to_id] += transaction.amount
            valid_transactions_for_longest_chain.append(transaction)

        # if len(valid_transactions_for_longest_chain) < config.BLOCK_TXNS_MIN_THRESHHOLD:
        # logger.debug("<num_txns> not enough txns to mine a block !!",)
        # return

        new_block = Block(
            parent_block,
            valid_transactions_for_longest_chain,
            simulation.clock,
            self.__peer_id,
            True,
        )
        self.__mining_new_blocks.append(new_block)
        new_event = Event(
            EventType.BLOCK_MINE_START,
            simulation.clock,
            0,
            self.__mine_block_start,
            (new_block,),
            f"attempt to mine block {new_block}",
        )
        simulation.enqueue(new_event)

    def __get_longest_chain(self):
        chain = []
        cur_chain = self.__longest_chain_leaf
        while cur_chain.prev_block:
            chain.append(cur_chain)
            cur_chain = cur_chain.prev_block
        return chain

    def validate_block(self, block: Block) -> bool:
        return self.__validate_block(block)

    def add_block_core(self, block: Block):
        self.__add_block(block)

    def override_mine_end_handler(self, fn):
        self.__mine_block_end_handler = fn

    def publish_block(self, block: Block):
        new_event = Event(
            EventType.BLOCK_BROADCAST,
            simulation.clock,
            0,
            self.__broadcast_block,
            (block,),
            f"{self.__peer_id}->* broadcast {block}",
        )
        simulation.enqueue(new_event)

    @property
    def branch_lengths(self):
        return self.__branch_lengths

    def __update_lead(self, delta):
        old_lead = self.lead
        new_lead = old_lead + delta
        logger.debug("%s Lead change %s %s", self.peer_id, self.lead, delta)
        # self.__change_lead((self.lead, new_lead))

        if delta == 0:
            raise NotImplementedError("Lead change of 0 not implemented")

        if delta > 0:
            # self.generate_block()
            self.lead = new_lead
            self.__current_parent_block = self.__secret_chain_leaf
            return

        # all below cases are for delta < 0 ie delta = -1
        if old_lead > 2:
            block = self.secret_blocks.pop(0)
            self.publish_block(block)
            self.__current_parent_block = self.__secret_chain_leaf

            new_lead -= 1

        elif old_lead == 2:
            for block in self.secret_blocks:
                self.publish_block(block)
            self.secret_blocks = []
            self.__current_parent_block = self.__secret_chain_leaf

            new_lead = 0

        elif old_lead == 1:
            for block in self.secret_blocks:
                self.publish_block(block)
            self.secret_blocks = []
            self.__current_parent_block = self.__secret_chain_leaf
            new_lead = -1

        elif old_lead == -1:
            new_lead = 0
            new_block = self.__blocks[-1]
            self.__current_parent_block = self.__blocks[-1]

        else:  # old_lead == 0
            for block in self.secret_blocks:
                self.__blocks.remove(block)
            self.secret_blocks = []
            self.__secret_chain_leaf = self.__longest_chain_leaf
            new_lead = 0
            self.__generate_block()

        self.lead = new_lead

    def flush_blocks(self):
        for block in self.__blocks:
            self.publish_block(block)

    def generate_block(self):
        return self.__generate_block()
