#!/usr/bin/env python
__author__ = 'James FitzGerald'

# Provides a basic shell interface demonstrating a sample client that makes use of the keyziio library
import cmd2
import restclient
import keyziio

class KzShell(cmd2.Cmd):

    intro = "Sample application using the keyziio service. Type help or ? to list commands.\n"
    prompt = 'keyziio-client> '

    def __init__(self):
        # Cmd is an old style class (not derived from object) so we have to use
        # _init_ directly
        cmd2.Cmd.__init__(self)
        self._logged_in = False
        self._username = None
        self._asp_rest_client = restclient.RestClient()
        self._asp_rest_client._server_port = 3000
        self._asp_rest_client._server_url = "localhost"
        self._keyziio = keyziio.Keyziio()

    def do_login(self, arg):
        'login: Logs the user in and sets up the users keyziio session.  Users are created automatically.  Usage: login <username>'
        if self._logged_in:
            print "Already logged in as {}".format(self._username)
            return

        print "logging {} in...".format(arg)
        try:
            response = self._asp_rest_client.api_call("GET", "user_keys/{}".format(arg)).json()
        except restclient.ConnectionFailure:
            print "Failed to connect to server for login"
            return

        self._keyziio.inject_user_key(response['private_key'], response['id'])
        self._username = arg
        self._logged_in = True
        print "Successfully retrieved user key and ignited keyziio client"
        print "done"

    def do_logout(self, arg):
        'logout: Logs the user out clearing the users keyziio session'
        if self._logged_in:
            print "Logging {} out...".format(self._username)
            self._logged_in = False
            self._username = None
            self._keyziio = keyziio.Keyziio()
            print "done"
        else:
            print "Try logging in first"

    def do_encrypt(self, arg):
        'encrypt: Encrypts input_file with key_id to output_file: Usage: encrypt <input_file> <output_file> <key_id>'
        if self._login_check():
            arg_split = arg.split()
            if len(arg_split) < 3:
                print "Invalid arguments.  Usage: encrypt <input_file> <output_file> <key_id>"
            else:
                print "encrypting {} with key:{}...".format(arg_split[0], arg_split[2])
                try:
                    self._keyziio.encrypt_file(*arg_split)
                except restclient.ServerFailure, restclient.ConnectionFailure:
                    print "Unable to encrypt.  Failed to connect to server"
                else:
                    print "done"

    def do_decrypt(self, arg):
        'decrypt: Decrypts input file to output file.  Gets the key_id from the file header.  Usage: decrypt <input_file> <output_file>'
        if self._login_check():
            arg_split = arg.split()
            if len(arg_split) < 2:
                print "Invalid arguments.  Usage: decrypt <input_file> <output_file>"
            else:
                print "decrypting {}...".format(arg_split[0])
                try:
                    self._keyziio.decrypt_file(*arg_split)
                except restclient.ServerFailure, keyziio.ConnectionFailure:
                    print "Unable to decrypt.  Failed to connect to server"
                else:
                    print "done"

    def _login_check(self):
        if not self._logged_in:
            print "You must be logged in to run the command."
        return self._logged_in

    def do_help(self, arg):
        if (arg == ""): #  Override the ugly looking standard help with cmd2
            print "Supported commands"
            print "=================="
            print self.do_login.__doc__
            print self.do_logout.__doc__
            print self.do_encrypt.__doc__
            print self.do_decrypt.__doc__

        else:
            cmd2.Cmd.do_help(self, arg)


def main():
    shell = KzShell()
    shell.cmdloop()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print "Operation failed: {}".format(e)
        exit(1)

