"""
Author: Tlams
Langage: Python
Minimum version require: 3.4

"""

import os
from Crypto.PublicKey import RSA
import hashlib


def encodepassphrase(passphrase):
    return hashlib.sha512(passphrase.encode("UTF-8")).hexdigest()


class CryticalData:
    def __init__(self):
        self.public_key = None
        self.private_key = None

    def generate_key(self, key_pvt, key_pub, passphrase, lgt=4096):
        try:
            private_key = RSA.generate(lgt)
            file = open(key_pvt, "wb")
            file.write(private_key.exportKey('PEM', passphrase, pkcs=1))
            file.close()

            public_key = private_key.publickey()
            file = open(key_pub, "wb")
            file.write(public_key.exportKey())
            file.close()

            os.chmod(key_pvt, 0o600)
            os.chmod(key_pub, 0o600)
            key_generation = {"result": "OK"}

        except BaseException as e:
            try:
                print("Clean...")
                os.remove(key_pvt)
                os.remove(key_pub)
            except OSError:
                pass

            key_generation = {
                "result": "ERROR",
                "type": "PYTHON",
                "value": "Key generation fail: {0}".format(e)
            }

        return key_generation

    def read_public_key(self, key_pub):
        try:
            file_key_pub = open(key_pub, "rb")
            self.public_key = RSA.importKey(file_key_pub.read())
            file_key_pub.close()
            result_public_key = {
                "result": "OK",
                "value": self.public_key
            }
        except BaseException as e:
            result_public_key = {
                "result": "ERROR",
                "type": "PYTHON",
                "value": "Your public key seem to invalid: {0}".format(e)
            }
        return result_public_key

    def read_private_key(self, key_pvt, passphrase):
        try:
            file_key_pvt = open(key_pvt, "rb")
            self.private_key = RSA.importKey(file_key_pvt.read(), passphrase)
            file_key_pvt.close()
            result_private_key = {
                "result": "OK",
                "value": self.private_key

            }
        except BaseException as e:
            result_private_key = {
                "result": "ERROR",
                "type": "PYTHON",
                "value": "Your private key seem to invalid: {0}".format(e)
            }
        return result_private_key

    def data_encryption(self, data, key=None):
        encfrypt = key.encrypt(data.encode("utf-8"), 64)
        try:
            if key:
                result_encrypt = {
                    "result": "OK",
                    "value":  encfrypt[0]
                }
            else:
                result_encrypt = {
                    "result": "OK",
                    "value": self.public_key.encrypt(data.encode("utf-8"), 64)
                }
        except BaseException as e:
            result_encrypt = {
                "result": "ERROR",
                "type": "PYTHON",
                "value": "Data encryption failed: {0}".format(e)
            }
        return result_encrypt

    def data_decryption(self, data, key=None):
        try:
            if key:
                result_decryption = {
                    "result": "OK",
                    "type": "PYTHON",
                    "value": key.decrypt(data)
                }
            else:
                result_decryption = {
                    "result": "OK",
                    "type": "PYTHON",
                    "value": self.private_key.decrypt(data)
                }
        except BaseException as e:
            result_decryption = {
                "result": "ERROR",
                "type": "PYTHON",
                "value": "Data decryption failed: {0}".format(e)
            }
        return result_decryption