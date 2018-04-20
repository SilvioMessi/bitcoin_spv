import os
import pickle

from bitcoin.core import b2x
import bitcoin.core
from bitcoin.core.script import CScript, OP_0, CScriptOp
from bitcoin.wallet import CBitcoinSecret


KEYS_STORE_FILE_PATH = "./keys.dat"

class Keys():
    
    def  __init__(self, path=KEYS_STORE_FILE_PATH):
        self.path = path
        self.keys = {}
        self.load_from_file()
        
    def load_from_file(self):
        if os.path.exists(self.path):
            with open(self.path, "rb") as f:
                self.keys = pickle.load(f)

    def save_to_file(self):
        with open(self.path, "wb") as f:
            pickle.dump(self.keys, f, pickle.HIGHEST_PROTOCOL)
    
    def add_private_key(self):
        seckey_str = input('\nInsert private key (WIF-compressed format):')
        if len(seckey_str) != 52 or (seckey_str[0] != 'K' and seckey_str[0] != 'L'):
            print("The key format is not valid!")
            return
        seckey = CBitcoinSecret(seckey_str)
        '''
        Calculate and store each data element of the scriptPubKey/scriptSig related to this private key.
        These data elements will be used in the Bloom Filters.
         
        From BIP 37:
        For each output, test each data element of the output script. This means each hash and key in the output script is tested independently. 
        For each input, test each data element of the input script (note: input scripts only ever contain data elements).
        
        The default scriptPubKey/scriptSig used by Bitcoin Core 0.16.0 are:
        - scriptPubKey: OP_HASH160 [20-byte-hash of {OP_0 hash160[pubkey]}] OP_EQUAL
        - scriptSig: 0x16 OP_0 hash160[pubkey]
        
        Note: 0x16 => The next opcode bytes is data to be pushed onto the stack

        The data element of the scriptSig should be only hash160[pubkey].
        Using only that data element the bloom filter doesn't work properly.
        Instead the filter works well using OP_0 hash160[pubkey].
        '''
        scriptPubKey_data_element = bitcoin.core.Hash160(CScript([OP_0, bitcoin.core.Hash160(seckey.pub)]))
        scriptSig_data_element = CScript([OP_0, bitcoin.core.Hash160(seckey.pub)])
        # Calculate and store also scriptPubKey/scriptSig
        scriptSig = CScript([CScriptOp(0x16), OP_0, bitcoin.core.Hash160(seckey.pub)])
        scriptPubKey = CScript([OP_0, bitcoin.core.Hash160(seckey.pub)]).to_p2sh_scriptPubKey()
        self.keys[seckey_str] = {
            "data_elements": [b2x(scriptPubKey_data_element), b2x(scriptSig_data_element)],
            "scriptSig" : b2x(scriptSig),
            "scriptPubKey" : b2x(scriptPubKey)
        }
        self.save_to_file()
        
    def get_data_elements_for_filter(self):
        data_elements = []
        for key in self.keys:
            for data_element in self.keys[key]['data_elements']:
                data_elements.append(data_element)
        return data_elements
    
    def get_scripts(self):
        scripts = []
        for key in self.keys:
            scripts.append(self.keys[key]['scriptSig'])
            scripts.append(self.keys[key]['scriptPubKey'])
        return scripts
