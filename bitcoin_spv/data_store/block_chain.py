import collections
import os
import pickle

from binarytree import Node
from bitcoin.core import b2lx
from bitcoin.core.serialize import Hash


GENESIS_BLOCK_HASH = "000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f"
GENESIS_BLOCK_MERKLE_ROOT = "4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b"
BLOCK_CHAIN_FILE_PATH = "./block_chain.dat"

class BlockChain():
    
    def  __init__(self, path=BLOCK_CHAIN_FILE_PATH):
        self.path = path
        self.block_chain = collections.OrderedDict()
        self.load_from_file()
        if self.get_size() == 0:
            # Add genesis block at the block chain
            self.block_chain[GENESIS_BLOCK_HASH] = {
                "previous_block_hash" : "00"*32,
                "merkle_root" : GENESIS_BLOCK_MERKLE_ROOT
            }
        
    def load_from_file(self):
        if os.path.exists(self.path):
            with open(self.path, "rb") as f:
                self.block_chain = pickle.load(f)

    def save_to_file(self):
        with open(self.path, "wb") as f:
            pickle.dump(self.block_chain, f, pickle.HIGHEST_PROTOCOL)
            
    def get_genesis_block_hash(self):
        return GENESIS_BLOCK_HASH
    
    def add_block(self, block_hash, previous_block_hash, merkle_tree):
        assert previous_block_hash == self.get_top_block_hash()
        self.block_chain[block_hash] = {
            "previous_block_hash" : previous_block_hash,
            "merkle_root" : merkle_tree
        }
        self.block_chain[previous_block_hash]["next_block_hash"] = block_hash
    
    def get_top_block_hash(self):
        return next(reversed(self.block_chain))

    def get_size(self):
        return len(self.block_chain)
    
    def get_next_block_hash(self, current_block_hash):
        if current_block_hash == None:
            return GENESIS_BLOCK_HASH
        if "next_block_hash" in self.block_chain[current_block_hash]:
            return self.block_chain[current_block_hash]["next_block_hash"]
        return None
    
    def get_next_n_blocks_hashes(self, start_block_hash, n):
        current_block_hash = start_block_hash
        blocks_hashes = []
        for _ in range(0, n):
            current_block_hash = self.get_next_block_hash(current_block_hash)
            if current_block_hash != None:
                blocks_hashes.append(current_block_hash)
            else:
                break
        return blocks_hashes
    
    def validate_merkle_block(self,
                              current_block_hash,
                              merkle_root,
                              total_transactions,
                              hashes,
                              flags):
        
        # Check coherence between the stored block header and the downloaded merkle block 
        block = self.block_chain[current_block_hash]
        assert block["merkle_root"] == merkle_root
        
        '''
        Read the section "Parsing a partial merkle tree object" of BIP 37 to understand 
        the following code
        '''
        hashes_list = []
        bit_list = []
        for _hash in hashes:
            hashes_list.append(_hash)
        raw_data = flags  # Flag bits, packed per 8 in a byte, least significant bit first (WTF)
        for i in range(0, len(raw_data)):
            byte_string = bin(raw_data[i])[2:].rjust(8, "0")[::-1]
            bit_list = bit_list + list(byte_string)

        leaves = []
        for i in range(0, total_transactions):
            leaves.append(Node(0))
        merkle_tree_root_node = self.build_merkle_tree_structure(leaves)
    
        # Transaction hashes that have matched with the bloom filter 
        # (some could be false positive)
        transaction_hashes = []  
        computed_merkle_root = b2lx(
            self.parse_partial_mekel_tree(
                merkle_tree_root_node,
                bit_list,
                hashes_list,
                transaction_hashes
            )
        )
        assert computed_merkle_root == merkle_root
        return transaction_hashes

    # Merkle tree utilities
    def parse_partial_mekel_tree(self, node, bit_list, hashes_list, transactions_hashes):
        flag = bit_list.pop(0)
        if (flag == "0"):
            return hashes_list.pop(0)
        if (flag == "1" and node.left is None):
            transaction_hash = hashes_list.pop(0)
            transactions_hashes.append(b2lx(transaction_hash))
            return transaction_hash
        hash_left = self.parse_partial_mekel_tree(node.left, bit_list, hashes_list, transactions_hashes)
        if node.right:
            hash_right = self.parse_partial_mekel_tree(node.right, bit_list, hashes_list, transactions_hashes)
        else:
            hash_right = hash_left
        return Hash(hash_left + hash_right)
     
    def build_merkle_tree_structure(self, nodes):
        new_nodes = []
        for i in range(0, len(nodes), 2):
            if (i + 1 == len(nodes)):
                new_node = Node(0)
                new_node.left = nodes[i]
                new_node.right = None
                new_nodes.append(new_node)
            else:
                new_node = Node(0)
                new_node.left = nodes[i]
                new_node.right = nodes[i + 1]
                new_nodes.append(new_node)
        if len(new_nodes) > 1:
            return self.build_merkle_tree_structure(new_nodes)
        else:
            # Return the root node of the merkle tree
            return new_nodes[0]
