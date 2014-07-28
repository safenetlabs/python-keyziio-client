__author__ = 'James FitzGerald'
""" Keyz Prototype """

import argparse
import os
import sys
import logging
import tarfile
import restclient
from Crypto.Cipher import AES
import base64
import shutil


def create_project(project):
    """ Create a tar of the project """
    # tar up the project file
    project_tar_name = "{}.raw".format(project)
    raw_tar = tarfile.TarFile(name=project_tar_name, mode="w")
    raw_tar.add(project)
    raw_tar.close()

    # now call into keyzio to create a key
    rest_client = restclient.RestClient()
    new_key_json = rest_client.get_new_key()

    encrypt_project(project, project_tar_name, new_key_json)
    os.remove(project_tar_name)



def extract_project(project_keyzio_name):
    # get the key id
    bits = project_keyzio_name.split('.')
    key_id = bits[-2]
    rest_client = restclient.RestClient()
    key_json = rest_client.get_key(key_id)
    raw_key = base64.b64decode(key_json['cipher_key'])
    raw_iv = base64.b64decode(key_json['cipher_iv'])
    cipher = AES.new(raw_key, AES.MODE_CBC, raw_iv)
    file_in = open(project_keyzio_name, 'rb')
    cipher_text = file_in.read()
    plain_text = cipher.decrypt(cipher_text)
    file_out_name = '{}.raw'.format(bits[0])
    file_out = open(file_out_name, 'wb')
    file_out.write(plain_text)

    # Now untar it
    raw_tar = tarfile.TarFile(name=file_out_name, mode="r")
    if not os.path.exists('out'):
        os.mkdir('out')
    raw_tar.extractall('out')
    raw_tar.close()
    os.remove(file_out_name)
    print "Extracted encrypted archive {}".format(file_out_name)



def encrypt_project(project, project_tar_name, new_key_json):
    # now encrypt it and store the key id in a file
    raw_key = base64.b64decode(new_key_json['cipher_key'])
    raw_iv = base64.b64decode(new_key_json['cipher_iv'])
    cipher = AES.new(raw_key, AES.MODE_CBC, raw_iv)
    file_in = open(project_tar_name, 'rb')
    plain_text = file_in.read()
    cipher_text = cipher.encrypt(plain_text)
    file_out_name = '{}.{}.keyzio'.format(project, new_key_json['id'])
    file_out = open(file_out_name, 'wb+')
    file_out.write(cipher_text)
    print "Created encrypted archive {}".format(file_out_name)


def setup_args(argv=None):
    parser = argparse.ArgumentParser(description='Keyz Prototype Command Line Arguments')
    parser.add_argument('--create', action='store_true')
    parser.add_argument('--extract', action='store_true')
    parser.add_argument('-project', help="Project directory name")
    #if argv:
    #    args = parser.parse_args(argv)
    #else:
    args = parser.parse_args()
    return args


def main(argv):
    args = setup_args(argv)
    if args.create:
        create_project(args.project)
    if args.extract:
        extract_project(args.project)


if __name__ == "__main__":
    try:
        main(sys.argv)
    except Exception as e:
        print e
    print "finished"



