from typing import Any
import logging

from Block import Block
from Transaction import CoinBaseTransaction
from DiscreteEventSim import simulation, Event, EventType
from BlockChainBase import BlockChainBase

logger = logging.getLogger(__name__)


class HonestBlockChain(BlockChainBase):

    def add_block(self, block: Block) -> bool:
        """
        validate and then add a block to the chain
        """
        if not self._validate_block(block):
            return False

        self._add_block(block)

        chain_len_upto_block = self._branch_lengths[block]
        self._validate_saved_blocks()
        if chain_len_upto_block > self._longest_chain_length:
            logger.debug(
                "%s <longest_chain> %s %s generating new block !!",
                self._peer_id,
                str(self._longest_chain_length),
                str(chain_len_upto_block),
            )
            self._longest_chain_length = chain_len_upto_block
            self._longest_chain_leaf = block
            self._generate_block()

    def _mine_block_end(self, block: Block):
        """
        Broadcast a block to all connected peers.
        """
        self._mining_new_blocks.remove(block)
        if block.prev_block == self._longest_chain_leaf and self._validate_block(block):
            logger.info(
                "%s <%s> %s", self._peer_id, EventType.BLOCK_MINE_SUCCESS, block
            )
            block.transactions.append(
                CoinBaseTransaction(self._peer_id, block.timestamp)
            )
            self._add_block(block)
            new_event = Event(
                EventType.BLOCK_MINE_SUCCESS,
                simulation.clock,
                0,
                self._mine_success_handler,
                (block,),
                f"{self._peer_id}->* broadcast {block}",
            )
            simulation.enqueue(new_event)
        else:
            # no longer longest chain
            logger.info("%s <%s> %s", self._peer_id, EventType.BLOCK_MINE_FAIL, block)
        logger.info("restarting block minining")
        # self._generate_block()

    def _generate_block(self) -> Block:
        """
        Generate a new block
        """
        sorted(self._new_transactions, key=lambda x: x.timestamp)
        valid_transactions_for_longest_chain = []
        balances_upto_block = self._branch_balances[self._longest_chain_leaf].copy()
        for transaction in self._new_transactions:
            if balances_upto_block[transaction.from_id] < transaction.amount:
                continue
            balances_upto_block[transaction.from_id] -= transaction.amount
            balances_upto_block[transaction.to_id] += transaction.amount
            valid_transactions_for_longest_chain.append(transaction)

        # if len(valid_transactions_for_longest_chain) < config.BLOCK_TXNS_MIN_THRESHHOLD:
        # logger.debug("<num_txns> not enough txns to mine a block !!",)
        # return

        new_block = Block(
            prev_block=self._longest_chain_leaf,
            transactions=valid_transactions_for_longest_chain,
            timestamp=simulation.clock,
            miner=self._peer_id,
            is_private=False,
        )
        self._mining_new_blocks.append(new_block)
        new_event = Event(
            EventType.BLOCK_MINE_START,
            simulation.clock,
            0,
            self._mine_block_start,
            (new_block,),
            f"attempt to mine block {new_block}",
        )
        simulation.enqueue(new_event)

    def _get_longest_chain(self):
        return self._get_chain(self._longest_chain_leaf)

    def publish_block(self, block: Block):
        new_event = Event(
            EventType.BLOCK_BROADCAST,
            simulation.clock,
            0,
            self._broadcast_block,
            (block,),
            f"{self._peer_id}->* broadcast {block}",
        )
        simulation.enqueue(new_event)
