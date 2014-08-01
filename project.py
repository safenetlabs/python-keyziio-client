__author__ = 'James FitzGerald'
""" Keyz Prototype """

import argparse
import os
import sys
import tarfile
#import restclient
#from Crypto.Cipher import AES
#import base64
import keyzio
import uuid


def create_project(project):
    """ Create a tar of the project """
    # tar up the project file
    project_tar_name = "{}.raw".format(project)
    raw_tar = tarfile.TarFile(name=project_tar_name, mode="w")
    raw_tar.add(project)
    raw_tar.close()
    # now call into keyzio to create a key and encrypt the tar file
    key_id = str(uuid.uuid4())
    file_out_name = '{}.{}.keyzio'.format(project, key_id)
    keyz = keyzio.KeyZIO()
    keyz.authenticate_with_oauth()
    keyz.new_key(key_id)
    keyz.encrypt_file(key_id, project_tar_name, file_out_name)
    os.remove(project_tar_name)


def extract_project(project_keyzio_name):
    # get the key id
    bits = project_keyzio_name.split('.')
    key_id = bits[-2]
    keyz = keyzio.KeyZIO()
    keyz.authenticate_with_oauth()
    file_out_name = '{}.{}.raw'.format(bits[0], key_id)
    keyz.decrypt_file(key_id, project_keyzio_name, file_out_name)
    # Now untar it
    raw_tar = tarfile.TarFile(name=file_out_name, mode="r")
    if not os.path.exists('out'):
        os.mkdir('out')
    raw_tar.extractall('out')
    raw_tar.close()
    os.remove(file_out_name)
    print "Extracted encrypted archive {}".format(file_out_name)


def setup_args():
    parser = argparse.ArgumentParser(description='Keyz Prototype Command Line Arguments')
    parser.add_argument('--create', action='store_true')
    parser.add_argument('--extract', action='store_true')
    parser.add_argument('-project', help="Project directory name")
    args = parser.parse_args()
    return args


def main():
    args = setup_args()
    if args.create:
        create_project(args.project)
    if args.extract:
        extract_project(args.project)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print e
    print "finished"



