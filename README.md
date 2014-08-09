keyzio_client
=============

Introduction
------------

The keyzio client library is intended to be integrated into applications wanting to encrypt or decrypt files using the keyzio service.
It includes a sample command shell application (kzshell.py) and the keyzio library itself which is currently exposed as a python module (keyzio.py)

Usage
-----
You need pip installed to install the requirements.  You can google this for yourself it will be fun.

* Install the python pre-requisites by executing the following command at the command line from the root directory of the repository:
<code>pip install -r requirements.txt</code>

* Get the ASP Server repository and run it according to its instructions (todo: add in the links).  The sample application expects the server to be running locally on port 3000 (ie. http://localserver:3000)

* On the command line execute:
<code>./kzshell.py</code>

* The shell should now be running.  Here are some basics to get you started:

<code>login some_username</code>

This will create a user if one does not exist and retrieve the users private key from the ASP (Application Service Provider) and injects it into the keyzio library.

<code>encrypt an_input_file an_output_file a_key_identifier</code>

This will encrypt 'an_input_file' with a key ientified by 'a_key_identifier' and write it to 'an_output_file'.  If the key does not exist it will be created.

<code>decrypt an_encrypted_input_file an_output_file</code>

This will decrypt the encrypted file 'an_encrypted_input_file' to 'an_output_file'. The key identifier is automatically extracted from the encrypted file.

<code>!ls</code>

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

Injects the users private key and id so that they can unwrap keyzio data keys.
The private key is expected to be in PEM format.



