import ctypes

class Transaction(ctypes.Structure):
    _fields_ = [
        ("sender", ctypes.c_char * 50),
        ("receiver", ctypes.c_char * 50),
        ("amount", ctypes.c_float)
    ]

class Block(ctypes.Structure):
    _fields_ = [
        ("index", ctypes.c_int),
        ("timestamp", ctypes.c_long),
        ("tx_count", ctypes.c_int),
        ("tx", Transaction * 5),  
        ("previous_hash", ctypes.c_char * 65), 
        ("hash", ctypes.c_char * 65),
        ("nonce", ctypes.c_int)              
    ]

class Blockchain(ctypes.Structure):
    _fields_ = [
        ("blocks", ctypes.POINTER(Block) * 1000),
        ("length", ctypes.c_int),
        ("difficulty", ctypes.c_int)
    ]
