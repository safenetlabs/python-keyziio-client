__author__ = 'James FitzGerald'
""" Client side API for Keyzio / AasMountain / AasGuard / Keyster etc.... """
import restclient
import base64
from Crypto.Cipher import AES

class KeyZIO(object):

    def __init__(self):
        self._rest_client = restclient.RestClient()

    def authenticate_with_oauth(self):
        # Not currently supported.. w.i.p
        # Authentication is currently not against the rest server but instead directly against the OAuth2 Auth Server
        # which is github in this hackathon
        import oauth2authenticate
        self._rest_client.set_oauth2_data(oauth2authenticate.authenticate())

    def authenticate(self, username, password):
        return self._rest_client.authenticate(username, password)

    def create_user(self, username, password):
        self._rest_client.create_user(username, password)

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
        cipher = self._init_cipher(key_id)
        # PKCS #7 padding
        pad_length = cipher.block_size - (len(data_in) % cipher.block_size)
        if pad_length == 0:
            pad_length = cipher.block_size
        data_in += chr(pad_length) * pad_length
        return cipher.encrypt(data_in)


    def decrypt(self, key_id, data_in):
        """ Returns plain text
        """
        cipher = self._init_cipher(key_id)
        data_out = cipher.decrypt(data_in)
        return data_out[:-ord(data_out[-1])]

    def _init_cipher(self, key_id):
        keys = self._rest_client.get_key(key_id)
        if len(keys) == 0:
            # create the key
            keys = self._rest_client.get_new_key(key_id)
        key_json = keys[0]
        raw_key = base64.b64decode(key_json['cipher_key'])
        raw_iv = base64.b64decode(key_json['cipher_iv'])
        return AES.new(raw_key, AES.MODE_CBC, raw_iv)