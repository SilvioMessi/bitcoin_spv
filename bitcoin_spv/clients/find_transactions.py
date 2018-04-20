from bitcoin.bloom import CBloomFilter
from bitcoin.core import x, lx, b2lx, b2x
from bitcoin.messages import msg_filterload, msg_getdata
from bitcoin.net import CInv

from .base_bitcoin import BaseBitcoinClient


class FindTransactionsClient(BaseBitcoinClient):
   
    def __init__(self, socket, parameters_store, block_chain, keys_store):
        super(FindTransactionsClient, self).__init__(socket)
        self.parameters_store = parameters_store
        self.block_chain = block_chain
        self.keys_store = keys_store
        self.data_elements = keys_store.get_data_elements_for_filter()
        self.my_scripts = keys_store.get_scripts()
        self.data_request = 0
        self.data_received = 0
        self.filtered_transation_hashes = []

    def handle_verack(self, _):
        self.find_transactions()

    def find_transactions(self):
        # Set bloom filter
        elements_in_the_filter = len(self.data_elements)
        false_positive_rate = 0.0000001
        msg = msg_filterload(elements_in_the_filter, false_positive_rate, 0, CBloomFilter.UPDATE_NONE)
        for data_element in self.data_elements:
            msg.insert(x(data_element))
        self.send_message(msg)
        # Request filtered data
        print("\nStarting the analysis of the block chain in order to find your transactions...")
        self.send_getdata()

    def send_getdata(self):
        start_block_hash = self.parameters_store.get_last_block_analized()
        block_hashes = self.block_chain.get_next_n_blocks_hashes(start_block_hash, 5000)
        if len(block_hashes) == 0:
            self.stop_client = True
            print("Analysis ended!")
        self.data_request = len(block_hashes)
        invs = []
        for block_hash in block_hashes:
            inv = CInv()
            '''
            MSG_FILTERED_BLOCK    
            Indicates the reply should be a merkleblock message rather than a block message; 
            this only works if a bloom filter has been set.
            '''
            inv.type = 3
            inv.hash = lx(block_hash)
            invs.append(inv)
        msg = msg_getdata()
        msg.inv = invs
        self.send_message(msg)

    def handle_merkleblock(self, message_obj):
        self.data_received += 1
        block_hash = b2lx(message_obj.merkleblock.GetHash())
        self.parameters_store.set_last_block_analized(block_hash)
        # If number of hashes in merkle block = 1, in hashes there is only the merkle root
        if len(message_obj.merkleblock.hashes) > 1:
            transition_hasesh = self.block_chain.validate_merkle_block(
                block_hash,
                b2lx(message_obj.merkleblock.hashMerkleRoot),
                message_obj.merkleblock.total_transactions,
                message_obj.merkleblock.hashes,
                message_obj.merkleblock.flags
            )
            # Store the filtered transition hashes (some could be false positive)
            # The peer will send all the info about these transitions (see method handle_tx)
            self.filtered_transation_hashes += transition_hasesh
        if self.data_received >= self.data_request:
            print("{} blocks analyzed".format(self.data_request))
            self.data_received = 0
            self.send_getdata()

    def handle_tx(self, message_obj):
        '''
        From BIP 37:
        Because a merkleblock message contains only a list of transaction hashes, 
        transactions matching the filter should also be sent in separate tx messages 
        after the merkleblock is sent. This avoids a slow roundtrip that would otherwise 
        be required.
        '''
        tx_hash = b2lx(message_obj.tx.GetHash())
        tx_id = b2lx(message_obj.tx.GetTxid())
        # Check if there are some false positive
        if tx_hash not in self.filtered_transation_hashes:
            return
        tx_is_mine = False
        for vin in message_obj.tx.vin:
            if b2x(vin.scriptSig) in self.my_scripts:
                tx_is_mine = True
                print ("Transaction ID {}".format(tx_id))
                print ("You spent the bitcoin earned from transaction with ID\n{} (vout index {})".format(
                    b2lx(vin.prevout.hash), 
                    vin.prevout.n)
                )
                print ("-"*100)
        for vout in message_obj.tx.vout:
            if b2x(vout.scriptPubKey) in self.my_scripts:
                tx_is_mine = True
                print ("Transaction ID {}".format(tx_id))
                print ("You earned {} bitcoin".format(vout.nValue))
                print ("-"*100)
        if tx_is_mine:
            # You can store the transition data in order to create your own wallet
            pass
