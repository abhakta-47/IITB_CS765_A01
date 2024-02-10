from typing import Any
import random
from copy import deepcopy
from functools import reduce
from Transaction import Transaction
import logging

from DiscreteEventSim import simulation, Event
import config
from utils import expon_distribution

logger = logging.getLogger(__name__)


class Block:

    def __init__(self, prev_block, transactions: list[Transaction], timestamp: float):
        self.block_id: int = random.randint(0, 1000000)
        self.prev_block: "Block" = prev_block
        self.transactions: list[Transaction] = transactions
        self.timestamp: float = timestamp

        self.prev_block_hash = hash(prev_block)

    @property
    def header(self) -> str:
        if len(self.transactions) == 0:
            return hash("genesis block")
        transaction_ids = reduce(
            lambda a, b: a+b, map(lambda x: x.txn_id, self.transactions))
        return f"{self.block_id}-{self.prev_block_hash}-{self.timestamp}-{transaction_ids}"

    def __hash__(self) -> int:
        return hash(self.header)

    def __repr__(self) -> str:
        return f"Block({self.block_id} 󰔛:{self.timestamp})"

    # def __str__(self) -> str:
    #     return f"Block id:{self.block_id} 󰔛:{self.timestamp} prev_hash:{self.prev_block_hash} txns:{self.transactions}"

    @property
    def size(self) -> int:
        '''
        size in kB
        '''
        return len(self.transactions)+1


class BlockChain:

    def __init__(self, cpu_power: float, broadcast_block_function: Any, peers: list[Any]):
        self.__blocks: list[Block] = []
        self.__new_transactions: list[Transaction] = []
        self.__block_arrival_time: dict[Block, float] = {}
        self.__broadcast_block: Any = broadcast_block_function

        self.__longest_chain_length: int = 0
        self.__longest_chain_leaf: Block = None

        self.__branch_lengths: dict[Block, int] = {}
        self.__branch_balances: dict[Block, dict[Any, int]] = {}
        self.__branch_transactions: dict[Block, list[Transaction]] = {}

        self.avg_interval_time = config.INITIAL_AVG_INTERVAL_TIME
        self.cpu_power: float = cpu_power

        self.__init_genesis_block(peers)

    def __init_genesis_block(self, peers: list[Any]):
        genesis_block = Block(None, [], 0)
        genesis_block.block_id = 0
        self.__blocks.append(genesis_block)
        self.__longest_chain_length = 1
        self.__longest_chain_leaf = genesis_block
        self.__branch_lengths[genesis_block] = 1
        self.__branch_transactions[genesis_block] = []
        self.__branch_balances[genesis_block] = {}
        for peer in peers:
            self.__branch_balances[genesis_block].update(
                {peer: config.INITIAL_COINS})

    def __validate_block(self, block: Block) -> bool:
        '''
        1. validate all transactions
        2. transactions are not repeated
        '''
        prev_block = block.prev_block
        for transaction in block.transactions:
            if not self.__validate_transaction(transaction, prev_block):
                return False
            if transaction in self.__branch_transactions[prev_block]:
                return False

        # logger.debug(f"Block {block} is valid")
        return True

    def __validate_transaction(self, transaction: Transaction, prev_block: Block) -> bool:
        '''
        1. no balance of any peer shouldn't go negative
        '''
        try:
            balances_upto_block = self.__branch_balances[prev_block]
        except Exception as e:
            # logger.debug(f"prev:{prev_block}; blanances:{self.__branch_balances}")
            exit(1)
        if balances_upto_block[transaction.from_id] < transaction.amount:
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
            balances_upto_block[transaction.from_id] -= transaction.amount
            balances_upto_block[transaction.to_id] += transaction.amount
        self.__branch_balances[block] = balances_upto_block
        # self.__branch_balances.pop(prev_block)
        # logger.debug(f"Balances upto block {block} are {balances_upto_block}")

    def __update_branch_transactions(self, block: Block):
        prev_block = block.prev_block
        self.__branch_transactions[block] = []
        for transaction in block.transactions:
            self.__branch_transactions[block].append(transaction)
        for transaction in self.__branch_transactions[prev_block]:
            self.__branch_transactions[block].append(transaction)
        # self.__branch_transactions.pop(prev_block)

    def __update_avg_interval_time(self, block: Block):
        prev_block = block.prev_block
        num_blocks = len(self.__blocks)
        if num_blocks == 1:
            return
        interval_time = block.timestamp - prev_block.timestamp
        self.avg_interval_time = (
            self.avg_interval_time * (num_blocks-1) + interval_time) / num_blocks
        logger.debug("Avg interval updated %s", self.avg_interval_time)

    def __update_block_arrival_time(self, block: Block):
        self.__block_arrival_time[block] = simulation.clock

    def __add_block(self, block: Block) -> bool:
        '''
        Add a block to the chain
        '''
        prev_block = block.prev_block
        if prev_block not in self.__blocks:
            return False

        self.__blocks.append(block)
        self.__update_chain_length(block)
        self.__update_balances(block)
        self.__update_branch_transactions(block)
        self.__update_block_arrival_time(block)
        self.__update_avg_interval_time(block)

    def add_block(self, block: Block) -> bool:
        '''
        validate and then add a block to the chain
        '''
        if not self.__validate_block(block):
            return False

        self.__add_block(block)

        chain_len_upto_block = self.__branch_lengths[block]
        if chain_len_upto_block > self.__longest_chain_length:
            self.__longest_chain_length = chain_len_upto_block
            self.__longest_chain_leaf = block
            logger.debug(f"new longest chain. generating new block !!")
            self.mine_block()

    def add_transaction(self, transaction: Transaction) -> bool:
        '''
        Add a transaction to the chain
        '''
        self.__new_transactions.append(transaction)
        if len(self.__new_transactions) > config.BLOCK_GEN_TRXN_THRESHOLD:
            logger.debug(f"Threshold reached. generating new block !!")
            self.mine_block()

    def broadcast_block(self, block: Block):
        '''
        Broadcast a block to all connected peers.
        '''
        if block.prev_block == self.__longest_chain_leaf:
            self.__add_block(block)
            logger.debug(f"mining successful. broadcasting block {block}")
            self.__broadcast_block(block)
            return
        logger.debug(f"mining failed. block {block} not broadcasted")

    def mine_block(self) -> Block:
        '''
        Generate a new block
        '''
        sorted(self.__new_transactions, key=lambda x: x.timestamp)
        valid_transactions_for_longest_chain = []
        balances_upto_block = self.__branch_balances[self.__longest_chain_leaf].copy(
        )
        for transaction in self.__new_transactions:
            if transaction in self.__branch_transactions[self.__longest_chain_leaf]:
                continue
            if balances_upto_block[transaction.from_id] < transaction.amount:
                continue
            balances_upto_block[transaction.from_id] -= transaction.amount
            balances_upto_block[transaction.to_id] += transaction.amount
            valid_transactions_for_longest_chain.append(transaction)

        new_block = Block(self.__longest_chain_leaf,
                          valid_transactions_for_longest_chain, simulation.clock)
        delay = expon_distribution(self.avg_interval_time/self.cpu_power)

        # self.broadcast_block(new_block)
        new_event = Event("start_block_mine", simulation.clock, delay,
                          self.broadcast_block, (new_block,), f"attempt to mine block {new_block}")
        simulation.enqueue(new_event)
