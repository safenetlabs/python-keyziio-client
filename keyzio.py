__author__ = 'James FitzGerald'
""" Client side API for Keyzio  """
import restclient
import base64
import os.path
from Crypto.Cipher import AES


class KeyZIO(object):

    CHUNK_LENGTH = 1024    # 1k at a time -- MUST BE A MULTIPLE OF CIPHER BLOCK SIZE (16 IN OUR CASE)

    def __init__(self):
        self._rest_client = restclient.RestClient()

    def authenticate_with_oauth(self):
        # Not currently supported.. w.i.p
        # Authentication is currently not against the rest server but instead directly against the OAuth2 Auth Server
        # which is github in this hackathon
        import oauth2authenticate
        self._rest_client.set_oauth2_data(oauth2authenticate.authenticate())

    def authenticate(self, username, password):
        self._rest_client.authenticate(username, password)

    def create_user(self, username, password):
        self._rest_client.create_user(username, password)

    def new_key(self, key_id):
        return self._rest_client.get_new_key(key_id)

    def _process_file(self, key_id, file_in, file_out, encrypt):
        cipher = self._init_cipher(key_id)
        plain_text_length = os.path.getsize(file_in)
        cipher_op = self._encrypt_chunk if encrypt else self._decrypt_chunk
        with open(file_in, 'rb') as f_in:
            with open(file_out, 'wb') as f_out:
                bytes_remaining = plain_text_length
                while bytes_remaining > 0:
                    bytes_to_read = bytes_remaining if bytes_remaining < self.CHUNK_LENGTH else self.CHUNK_LENGTH
                    data_in = f_in.read(bytes_to_read)
                    bytes_remaining -= bytes_to_read
                    f_out.write(cipher_op(cipher, data_in, bytes_remaining <= 0 ))


    def encrypt_file(self, key_id, file_in, file_out):
        self._process_file(key_id, file_in, file_out, encrypt=True)

    def decrypt_file(self, key_id, file_in, file_out):
        self._process_file(key_id, file_in, file_out, encrypt=False)

    def encrypt(self, key_id, data_in):
        """ Returns cipher text
        """
        cipher = self._init_cipher(key_id)
        return self._encrypt_chunk(cipher, data_in)

    def _encrypt_chunk(self, cipher, data_in, is_last_chunk):
        if is_last_chunk:
            pad_length = cipher.block_size - (len(data_in) % cipher.block_size)
            if pad_length == 0:
                pad_length = cipher.block_size
            data_in += chr(pad_length) * pad_length
        return cipher.encrypt(data_in)

    def _decrypt_chunk(self, cipher, data_in, is_last_chunk):
        data_out = cipher.decrypt(data_in)
        return data_out if not is_last_chunk else data_out[:-ord(data_out[-1])]

    def decrypt(self, key_id, data_in):
        """ Returns plain text
        """
        cipher = self._init_cipher(key_id)
        return self._decrypt_chunk(cipher, data_in)

    def _init_cipher(self, key_id):
        keys = self._rest_client.get_key(key_id)
        if len(keys) == 0:
            # create the key
            key_json = self._rest_client.get_new_key(key_id)
        else:
            key_json = keys[0]
        raw_key = base64.b64decode(key_json['cipher_key'])
        raw_iv = base64.b64decode(key_json['cipher_iv'])
        return AES.new(raw_key, AES.MODE_CBC, raw_iv)