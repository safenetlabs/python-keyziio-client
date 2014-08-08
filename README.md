keyzio_client
=============

Introduction
------------

The keyzio client library is intended to be integrated applications wanting to encrypt/decrypt files using the keyzio service.
It includes a sample command shell application (kzshell.py) and the keyzio library itself which is currently exposed as a python module (keyzio.py)

Usage
-----
You need pip installed to install the requirements.  You can google this for yourself it will be fun.

* Install the python pre-requisites by executing the following command at the command line from the keyzio_client directory:
> pip install -r requirements.txt

* On the command line execute:
> ./kzshell.py

* The shell should now be running.  Here are some basics to get you started:

> login some_username
This will create a user if one does not exist and retrieve the users private key from the ASP (Application Service Provider) and injects
it into the keyzio library.

> encrypt an_input_file an_output_file a_key_identifier
This will encrypt 'an_input_file' with a key ientified by 'a_key_identifier' and write it to 'an_output_file'.  If the key does not exist it will be created.

> decrypt an_encrypted_input_file an_output_file
This will decrypt the encrypted file 'an_encrypted_input_file' to 'an_output_file'.  The key identifier is automatically extracted from the encrypted file.

> !ls
The '!' character will allow you to execute shell commands like 'ls' pretty cool huh!

Keyzio API
----------

The API is exposed via the keyzio module.

**class keyzio.Keyzio** 

*Methods*

<code>__init__(self)</code>

<code>decrypt_file(self, file_in, file_out)</code>

Decrypts file_in using key_id.  It will create the key if it has to.

<code>encrypt_file(self, file_in, file_out, key_id)</code>

Encrypts file_in using key_id.  It will create the key if it has to.

<code>inject_user_key(self, user_private_key_pem, user_id)</code>

Injects the users private key and id so that they can unwrap keyzio data keys
The private key is expected to be in PEM format



