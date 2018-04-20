import socket

from bitcoin_spv.clients import SynchronizeBlockChainClient, FindTransactionsClient
from bitcoin_spv.data_store import BlockChain, Parameters, Keys


if __name__ == "__main__":
    # Initialize all the data store components
    parameters_store = Parameters()
    block_chain = BlockChain()
    keys_store = Keys()
    
    # Connect to a bitcoin peer
    # In a real application you must connect and get data from 
    # multiple peer to avoid malicious peers
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("bitcoin.sipa.be", 8333))
    
    # Synchronize the block chain
    sync_client = SynchronizeBlockChainClient(sock, block_chain)
    sync_client.handshake() 
    # The method sync_client.sync_block_chain() is automatically called only 
    # when the "verack" message is received
    sync_client.run()
    
    # Add your private key
    keys_store.add_private_key()
    
    # The analysis of the block chain is quite slow
    # You can avoid to the searching from the genesis block
    parameters_store.set_last_block_analized("00000000000000000038816db4417466939fb975b768cee078e3842439d3e7a1")
    
    # Find your transactions
    find_client = FindTransactionsClient(sock, parameters_store, block_chain, keys_store)
    # The method find_client.handshake() must not be called because the previous socket 
    # is used. We must manually call the method find_client.find_transactions()
    find_client.find_transactions()
    find_client.run()
    find_client.close_stream()
