__author__ = 'James FitzGerald'
""" Client side API for Keyzio / AasMountain / AasGuard / Keyster etc.... """
import restclient
import base64
from Crypto.Cipher import AES

class KeyZIO(object):

    def __init__(self):
        self._rest_client = restclient.RestClient()

    def new_key(self, key_id):
        return self._rest_client.get_new_key(key_id)

    def encrypt_file(self, key_id, file_in, file_out):
        # TODO : this is not optimized, it will read all the file and write all the file in one swoop
        with open(file_in, 'rb') as f:
            plain_text = f.read()
        cipher_text = self.encrypt(key_id, plain_text)
        with open(file_out, 'wb') as f:
            f.write(cipher_text)

    def decrypt_file(self, key_id, file_in, file_out):
        # TODO : this is not optimized, it will read all the file and write all the file in one swoop
        with open(file_in, 'rb') as f:
            cipher_text = f.read()
        plain_text = self.decrypt(key_id, cipher_text)
        with open(file_out, 'wb') as f:
            f.write(plain_text)

    def encrypt(self, key_id, data_in):
        """ Returns cipher text
        """
        return self._init_cipher(key_id).encrypt(data_in)

    def decrypt(self, key_id, data_in):
        """ Returns plain text
        """
        return self._init_cipher(key_id).decrypt(data_in)

    def _init_cipher(self, key_id):
        key_json = self._rest_client.get_key(key_id)
        raw_key = base64.b64decode(key_json['cipher_key'])
        raw_iv = base64.b64decode(key_json['cipher_iv'])
        return AES.new(raw_key, AES.MODE_CBC, raw_iv)