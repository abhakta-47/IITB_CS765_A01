from typing import Any
import logging

from Block import Block
from Transaction import CoinBaseTransaction
from DiscreteEventSim import simulation, Event, EventType
from BlockChainBase import BlockChainBase

logger = logging.getLogger(__name__)


class PrivateBlockChain(BlockChainBase):
    def __init__(
        self,
        cpu_power: float,
        broadcast_block_function: Any,
        peers: list[Any],
        owner_peer: Any,
    ):
        super().__init__(cpu_power, broadcast_block_function, peers, owner_peer)

        self._secret_chain_leaf: Block = None

        self._current_parent_block: Block = None

        self.secret_blocks: list[Block] = []
        self.lead: int = 0

        self._current_parent_block = self._longest_chain_leaf
        self._generate_block()

    def add_block(self, block: Block) -> bool:
        """
        validate and then add a block to the chain
        """
        if not self._validate_block(block):
            return False

        self._add_block(block)

        self._validate_saved_blocks()

        if block.miner == self._peer_id:
            self._secret_chain_leaf = block
            self._update_lead(1)
        elif self._longest_chain_length < self._branch_lengths[block]:
            self._longest_chain_length = self._branch_lengths[block]
            self._longest_chain_leaf = block
            self._update_lead(-1)

    def _mine_block_end(self, block: Block):
        """
        Broadcast a block to all connected peers.
        """
        self._mining_new_blocks.remove(block)
        if block.prev_block == self._current_parent_block and self._validate_block(
            block
        ):
            logger.info(
                "%s <%s> %s", self._peer_id, EventType.BLOCK_MINE_SUCCESS, block
            )
            block.transactions.append(
                CoinBaseTransaction(self._peer_id, block.timestamp)
            )
            self.secret_blocks.append(block)
            self.add_block(block)
            new_event = Event(
                EventType.BLOCK_MINE_SUCCESS,
                simulation.clock,
                0,
                self._mine_success_handler,
                (block,),
                f"{self._peer_id}->* broadcast {block}",
            )
            simulation.enqueue(new_event)
            # if len(self._blocks) > config.MAX_NUM_BLOCKS:
            # simulation.stop_sim = True
        else:
            # no longer longest chain
            logger.info("%s <%s> %s", self._peer_id, EventType.BLOCK_MINE_FAIL, block)
            # self.generate_block()
        # logger.info("restarting block minining")
        self._generate_block()

    def _generate_block(self) -> Block:
        """
        Generate a new block
        """
        sorted(self._new_transactions, key=lambda x: x.timestamp)
        valid_transactions_for_longest_chain = []
        # if len(self.secret_blocks):
        # parent_block = self.secret_blocks[-1]
        # else:

        parent_block = self._current_parent_block
        balances_upto_block = self._branch_balances[parent_block].copy()
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
            prev_block=parent_block,
            transactions=valid_transactions_for_longest_chain,
            timestamp=simulation.clock,
            miner=self._peer_id,
            is_private=True,
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
        chain1 = self._get_chain(self._longest_chain_leaf)
        chain2 = self._get_chain(self._secret_chain_leaf)
        return chain1 if len(chain1) > len(chain2) else chain2

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

    @property
    def branch_lengths(self):
        return self._branch_lengths

    def _update_lead(self, delta):
        old_lead = self.lead
        new_lead = old_lead + delta
        logger.debug("%s Lead change %s %s", self.peer_id, self.lead, delta)
        # self._change_lead((self.lead, new_lead))

        if delta == 0:
            raise NotImplementedError("Lead change of 0 not implemented")

        if delta > 0:
            # self.generate_block()
            self.lead = new_lead
            self._current_parent_block = self._secret_chain_leaf
            return

        # all below cases are for delta < 0 ie delta = -1
        if old_lead > 2:
            block = self.secret_blocks.pop(0)
            self.publish_block(block)
            self._current_parent_block = self._secret_chain_leaf

            new_lead -= 1

        elif old_lead == 2:
            for block in self.secret_blocks:
                self.publish_block(block)
            self.secret_blocks = []
            self._current_parent_block = self._secret_chain_leaf

            new_lead = 0

        elif old_lead == 1:
            for block in self.secret_blocks:
                self.publish_block(block)
            self.secret_blocks = []
            self._current_parent_block = self._secret_chain_leaf
            new_lead = -1

        elif old_lead == -1:
            new_lead = 0
            new_block = self._blocks[-1]
            self._current_parent_block = self._blocks[-1]

        else:  # old_lead == 0
            for block in self.secret_blocks:
                self._blocks.remove(block)
            self.secret_blocks = []
            self._secret_chain_leaf = self._longest_chain_leaf
            new_lead = 0
            self._generate_block()

        self.lead = new_lead
