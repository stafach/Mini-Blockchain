import ctypes

class Block(ctypes.Structure):
    _fields_ = [
        ("index", ctypes.c_int),
        ("timestamp", ctypes.c_long),
        ("data", ctypes.c_char * 256),  
        ("previous_hash", ctypes.c_char * 65), 
        ("hash", ctypes.c_char * 65),
        ("nonce", ctypes.c_int),
        ("prev", ctypes.c_void_p)               
    ]

class Blockchain(ctypes.Structure):
    _fields_ = [
        ("blocks", ctypes.POINTER(Block) * 1000),
        ("length", ctypes.c_int),
        ("difficulty", ctypes.c_int)
    ]
