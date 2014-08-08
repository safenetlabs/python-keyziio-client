__author__ = 'James FitzGerald'

# Provides a basic shell interface demonstrating a sample client that makes use of the keyzio library
from cmd2 import Cmd
import restclient
import keyzio


class KzShell(Cmd):

    intro = "Sample application using the Keyzio service.  Type help or ? to list commands.\n"
    prompt = '(ezpz) '
    #file = None

    def __init__(self):
        # Cmd is an old style class (not derived from object) so we have to use
        # _init_ directly
        Cmd.__init__(self, None, None)
        self._logged_in = False
        # todo: Clean up use of rest client for ASP purposes
        self._asp_rest_client = restclient.RestClient()
        self._asp_rest_client._server_port = 3000
        self._asp_rest_client._server_url = "localhost"
        self._keyzio = keyzio.KeyZIO()

    def do_login(self, arg):
        'Logs the user in and sets up the users keyzio session: login-user username'
        print "logging {} in...".format(arg)
        response = self._asp_rest_client.api_call("GET", "user_keys/{}".format(arg)).json()
        self._keyzio.inject_user_key(response['private_key'], response['id'])
        self._logged_in = True
        print "Successfully retrieved user key and ignited keyzio client"
        print "done"


    def do_encrypt(self, arg):
        'Encrypts input_file with key_id to output_file: encrypt input_file output_file key_id'
        if self._login_check():
            arg_split = arg.split()
            if len(arg_split) < 3:
                print "Invalid arguments.  Usage: encrypt input_file output_file key_id"
            else:
                print "encrypting {} with key:{}...".format(arg_split[0], arg_split[2])
                self._keyzio.encrypt_file(*arg_split)
                print "done"

    def do_decrypt(self, arg):
        'Decrypts input file to output file.  Gets the key_id from the file header'
        if self._login_check():
            arg_split = arg.split()
            if len(arg_split) < 2:
                print "Invalid arguments.  Usage: decrypt input_file output_file"
            else:
                print "decrypting {}...".format(arg_split[0])
                self._keyzio.decrypt_file(*arg_split)
                print "done"

    def _login_check(self):
        if not self._logged_in:
            print "You need to login first"
        return self._logged_in


def main():
    shell = KzShell()
    shell.cmdloop()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print "Operation failed: {}".format(e)
        exit(1)


