import os
import pickle


PARAMETERS_STORE_FILE_PATH = "./parameters.dat"

class Parameters():
    
    def  __init__(self, path=PARAMETERS_STORE_FILE_PATH):
        self.path = path
        self.parameters = {
            "last_block_analized": None
        }
        self.load_from_file()
        
    def load_from_file(self):
        if os.path.exists(self.path):
            with open(self.path, "rb") as f:
                self.parameters = pickle.load(f)

    def save_to_file(self):
        with open(self.path, "wb") as f:
            pickle.dump(self.parameters, f, pickle.HIGHEST_PROTOCOL)
    
    def get_last_block_analized(self):
        return self.parameters["last_block_analized"]
    
    def set_last_block_analized(self, block_hash):
        self.parameters["last_block_analized"] = block_hash
        self.save_to_file()