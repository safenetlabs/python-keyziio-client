__author__ = 'James FitzGerald'
import struct
import json

class KeyzioDecodeException(Exception):
    """ File is either not a keyzio file or does not have a valid header """
    pass

class UnsupportedKeyzioVersionException(Exception):
    """ File is a newer version then this client can work with """
    pass


class Header(object):
    """
    The header is not a fixed length.  The format is as follows:
        Prelude : 128 byte string
        Magic Number: 32 byte string preset as "d371004cba8d4fafaeb324f72a52d91b"
        Version: 4 byte unsigned long
        Length: Length of the header data (the rest of the header)
        Header Data: Variable length string containing json encoded header data.  It currently just includes a 'key_id'
         key/value pair.
    """
    _PRELUDE_FORMAT = "<128s"
    _MAGIC_NUMBER_FORMAT = "<32s"
    _VERSION_FORMAT = "<L"
    _LENGTH_FORMAT = "<L"

    _MAGIC_NUMBER = "d371004cba8d4fafaeb324f72a52d91b"
    _VERSION = 1

    def __init__(self):
        super(Header, self).__init__()
        self._prelude = "www.keyzio.com Encrypted File"
        self._key_id = None
        self._version = self._VERSION

    @property
    def prelude(self):
        return self._prelude

    @prelude.setter
    def prelude(self, value):
        # todo: add in a size check here
        self._prelude = value

    @property
    def key_id(self):
        return self._key_id

    @key_id.setter
    def key_id(self, value):
        self._key_id = value

    def decode_from_file(self, file):
        """ decodes the header from a file.  If the file is not a keyzio file we will throw a KeyzioDecodeException """
        pass

    def encode(self):
        """ returns a packed header """
        packed_prelude = struct.pack(self._PRELUDE_FORMAT, self._prelude)
        packed_magic_number = struct.pack(self._MAGIC_NUMBER_FORMAT, self._MAGIC_NUMBER)
        packed_version = struct.pack(self._VERSION_FORMAT, self._VERSION)
        header_content = json.dumps({'key_id':self._key_id})
        packed_header_content = struct.pack("<{}s".format(len(header_content)), header_content)
        packed_length = struct.pack(self._LENGTH_FORMAT, len(packed_header_content))
        return packed_prelude + packed_magic_number + packed_version + packed_length + packed_header_content


    def decode(self, packed_header):
        """ decodes a packed header """
        offset = 0
        # prelude
        self._prelude = struct.unpack_from(self._PRELUDE_FORMAT, packed_header, offset)[0]
        offset += struct.calcsize(self._PRELUDE_FORMAT)
        # magic number
        magic_number = struct.unpack_from(self._MAGIC_NUMBER_FORMAT, packed_header, offset)[0]
        offset += struct.calcsize(self._MAGIC_NUMBER_FORMAT)
        if (magic_number != self._MAGIC_NUMBER):
            raise KeyzioDecodeException
        # version
        self._version = struct.unpack_from(self._VERSION_FORMAT, packed_header, offset)[0]
        offset += struct.calcsize(self._VERSION_FORMAT)
        if (self._version > self._VERSION):
            raise UnsupportedKeyzioVersionException
        # length
        length = struct.unpack_from(self._LENGTH_FORMAT, packed_header, offset)[0]
        offset += struct.calcsize(self._LENGTH_FORMAT)

        # header-data
        header_data = struct.unpack_from("<{}s".format(length), packed_header, offset)[0]
        self._key_id = json.loads(header_data)['key_id']


if __name__ == "__main__":
    # just for debugging...
    h1 = Header()
    h1.key_id = "mah key John Snow"
    encoded_h1 = h1.encode()

    h2 = Header()
    h2.decode(encoded_h1)

    if (h1.key_id == h2.key_id):
        print "they match"
    else:
        print "no match"