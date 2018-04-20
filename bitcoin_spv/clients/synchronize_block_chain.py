from bitcoin.core import b2lx, lx
from bitcoin.messages import msg_getheaders
from bitcoin.net import CBlockLocator

from .base_bitcoin import BaseBitcoinClient


class SynchronizeBlockChainClient(BaseBitcoinClient):
    
    def __init__(self, socket, block_chain):
        super(SynchronizeBlockChainClient, self).__init__(socket)
        self.block_chain = block_chain
        self.new_block_headers_count = 0
    
    def handle_headers(self, message_header):
        for block_header in message_header.headers:
            self.block_chain.add_block(
                b2lx(block_header.GetHash()),
                b2lx(block_header.hashPrevBlock),
                b2lx(block_header.hashMerkleRoot))
        if len(message_header.headers) > 0 :
            self.new_block_headers_count += len(message_header.headers)
            # Try to download other block headers from the peer
            self.send_getheaders(self.block_chain.get_top_block_hash())
            print("{} block headers downloaded".format(self.new_block_headers_count))
        else:
            print("Synchronization ended! There are {} blocks in the bitcoin block chain".format(self.block_chain.get_size()))
            self.block_chain.save_to_file()
            self.stop_client = True

    def send_getheaders(self, block_hash_string):
        locator = CBlockLocator()
        locator.vHave = [lx(block_hash_string)]
        msg = msg_getheaders()
        msg.locator = locator
        self.send_message(msg)

    def handle_verack(self, _):
        self.sync_block_chain()
        
    def sync_block_chain(self):
        if self.block_chain.get_size() == 1:
            print("Starting the synchronization from the genesis block...")
        else:
            print ("Loaded {} block headers from data store. Starting the synchronization...".format(self.block_chain.get_size()))
        self.send_getheaders(self.block_chain.get_top_block_hash())