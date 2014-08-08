__author__ = 'James FitzGerald'

import restclient
import kzheader
import base64
import os.path
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, PKCS1_v1_5
#import random
import os
import binascii

from kzheader import KeyzioDecodeException

class InvalidKeyException(Exception):
    """ Cannot unwrap this key  """
    def __str__(self):
        return "Cannot unwrap this key"

class KeyZIO(object):
    """
    Client side API for Keyzio
    ... more details to be added on usage ...
    """
    CHUNK_LENGTH = 1024    # 1k at a time -- MUST BE A MULTIPLE OF CIPHER BLOCK SIZE (16 IN OUR CASE)

    def __init__(self):
        self._rest_client = restclient.RestClient()

    def inject_user_key(self, user_private_key_pem, user_id):
        self._user_private_key =  RSA.importKey(user_private_key_pem)
        self._user_id = user_id

    def _process_file(self, file_in, file_out, encrypt, key_id=None):
        if not encrypt:
            # get the key id from the file itself
            header = kzheader.Header()
            header_length = header.decode_from_file(file_in)
            key_id = header.key_id
        cipher = self._init_cipher(key_id)
        plain_text_length = os.path.getsize(file_in)
        cipher_op = self._encrypt_chunk if encrypt else self._decrypt_chunk
        with open(file_in, 'rb') as f_in:
            if not encrypt:
                f_in.seek(header_length)
            with open(file_out, 'wb') as f_out:
                if encrypt:
                    # create a header
                    header = kzheader.Header()
                    header.key_id = key_id
                    f_out.write(header.encode())
                bytes_remaining = plain_text_length
                while bytes_remaining > 0:
                    bytes_to_read = bytes_remaining if bytes_remaining < self.CHUNK_LENGTH else self.CHUNK_LENGTH
                    data_in = f_in.read(bytes_to_read)
                    bytes_remaining -= bytes_to_read
                    f_out.write(cipher_op(cipher, data_in, bytes_remaining <= 0 ))

    def encrypt_file(self, file_in, file_out, key_id):
        """ Encrypts file_in using key_id.  It will create the key if it has to. """
        self._process_file(file_in, file_out, True, key_id)

    def decrypt_file(self, file_in, file_out):
        """ Decrypts file_in using key_id.  It will create the key if it has to. """
        self._process_file(file_in, file_out, False)

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

    def _init_cipher(self, key_id):
        key_json = self._rest_client.get_key(key_id, self._user_id)
        # Key is encrypted under the user key, we have to decrypt it

        # todo: Should be an OAEP Cipher or better
        #oaep_cipher = PKCS1_OAEP.new(self._user_private_key)
        p15cipher = PKCS1_v1_5.new(self._user_private_key)
        wrapped_key = base64.b64decode(key_json['key'])

        # Stupid api - create a random for sentinel
        sentinel = binascii.b2a_hex(os.urandom(64))
        raw_key = p15cipher.decrypt(wrapped_key, sentinel)
        if raw_key == sentinel:
            raise InvalidKeyException()
        iv = base64.b64decode(key_json['iv'])
        return AES.new(raw_key, AES.MODE_CBC, iv)