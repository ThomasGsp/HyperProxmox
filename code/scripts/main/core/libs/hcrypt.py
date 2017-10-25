from core.modules.mod_access import *
import base64

def pcrypt(data, key):
    CritConf = CryticalData()
    data = CritConf.data_encryption(data, key)
    return data

def pdecrypt(data, key):
    CritConf = CryticalData()
    data = CritConf.data_decryption(data, key)
    return data