__author__ = 'James FitzGerald'

import argparse
import keyzio

def _setup_args():
    parser = argparse.ArgumentParser(description='Keyz Command Line Wrapper Arguments')
    parser.add_argument('-c', '--create-user', action='store_true')
    parser.add_argument('-e', '--encrypt-file', nargs=2, help="input_file output_file")
    parser.add_argument('-d', '--decrypt-file', nargs=2, help="input_file output_file")
    parser.add_argument('-k', '--key-id', help="key identifier")
    parser.add_argument('-u', '--username', help="users name")
    parser.add_argument('-p', '--password', help="users password")
    return parser.parse_args()

def main():
    _keyzio_api = keyzio.KeyZIO()
    args = _setup_args()
    if args.create_user:
        _keyzio_api.create_user(args.username, args.password)
    if args.encrypt_file or args.decrypt_file:
        if not _keyzio_api.authenticate(args.username, args.password):
            print "Authentication failed"
        else:
            if args.encrypt_file:
                _keyzio_api.encrypt_file(args.key_id, args.encrypt_file[0], args.encrypt_file[1])
            if args.decrypt_file:
                _keyzio_api.decrypt_file(args.key_id, args.decrypt_file[0], args.decrypt_file[1])

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print e
    print "finished"