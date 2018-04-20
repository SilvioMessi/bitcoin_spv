from _io import BytesIO

from bitcoin.core.serialize import SerializationTruncationError
from bitcoin.messages import msg_version, msg_verack, msg_pong, MsgSerializable


class BaseBitcoinClient(object):

    def __init__(self, socket):
        self.socket = socket
        self.buffer = BytesIO()
        self.stop_client = False

    def close_stream(self):
        self.socket.close()

    def send_message(self, message):
        self.socket.sendall(message.to_bytes())
        
    def handshake(self):
        # Send a "version" message to start the handshake
        msg = msg_version()
        # See BIP 111 (https://github.com/bitcoin/bips/blob/master/bip-0111.mediawiki)
        msg.nVersion = 70011
        msg.fRelay = False  # If false then broadcast transactions will not be announced until a filter{load,add,clear} command is received 
        self.send_message(msg)

    def handle_version(self, _):
        # Respond with a "verack" message to a "version" message
        msg = msg_verack()
        self.send_message(msg)
    
    def handle_ping(self, ping_message):
        # Respond with a pong message to a ping message
        msg = msg_pong()
        msg.nonce = ping_message.nonce
        self.send_message(msg)

    def run(self):
        while self.stop_client != True:
            # Read and store the data from the socket
            data = self.socket.recv(64)
            self.buffer.write(data)
            try:
                # Go at the beginning of the buffer
                self.buffer.seek(0)   
                # Deserialize the message         
                message = MsgSerializable().stream_deserialize(self.buffer)
                # Reset the buffer
                remaining = self.buffer.read()
                self.buffer = BytesIO()
                self.buffer.write(remaining)
                # Call handle function
                if message is not None:
                    handle_func_name = "handle_" + message.command.decode("utf-8")
                    handle_func = getattr(self, handle_func_name, None)
                    if handle_func:
                        handle_func(message)
            except SerializationTruncationError:
                # Read more data from the socket
                pass