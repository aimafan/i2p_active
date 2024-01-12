import os
import time
from Crypto.Cipher import AES
from Crypto.Cipher import ChaCha20_Poly1305
from Crypto.Random import get_random_bytes
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
import hashlib
import hmac
import struct
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from .connection import logger


class NTCP2Establisher():
    NTCP2_SESSION_REQUEST_MAX_SIZE = 287
    def __init__(self, m_RemoteIdentHash, m_IV, m_remoteStaticKey):
        self.m_RemoteIdentHash = m_RemoteIdentHash  # Bob的Hash
        self.m_IV = m_IV                            # Bob的IV
        self.my_key = my_X25519()
        self.m_remoteStaticKey = m_remoteStaticKey

    def CreateSessionRequestMessage(self):
        # 共有三个部分：
        # 1. obfuscated with RH_B  AES-CBC-256 encrypted X (32 bytes)       
        # 2. ChaChaPoly frame (32 bytes) k defined in KDF for message 1
        # 3. unencrypted authenticated  padding (optional)  length defined in options block

        # 关于第二部分option部分，共16字节，主要由以下几个部分
        # +----+----+----+----+----+----+----+----+
        # | id | ver|  padLen | m3p2len | Rsvd(0) |
        # +----+----+----+----+----+----+----+----+
        # |        tsA        |   Reserved (0)    |
        # +----+----+----+----+----+----+----+----+
        
        paddingLength = os.urandom(1)[0] % (self.NTCP2_SESSION_REQUEST_MAX_SIZE - 64)
        m_SessionRequestBufferLen = paddingLength + 64      # 会话请求缓冲区的长度
        self.m_SessionRequestBuffer = bytearray(m_SessionRequestBufferLen)
        self.m_SessionRequestBuffer[64: 64+paddingLength] = get_random_bytes(paddingLength) # 会话请求的缓冲区

        # 加密X
        # AES-256-CBC 加密
        encryption = AES.new(self.m_RemoteIdentHash, AES.MODE_CBC, self.m_IV)
        self.m_SessionRequestBuffer[:32] = encryption.encrypt(self.my_key.get_public_byte())  # 加密Alice的公钥

        self.KDF1Alice()

        options = bytearray(16)
        options[0] = 2  # 假定网络ID为2
        options[1] = 2  # 版本
        options[2:4] = paddingLength.to_bytes(2, 'big')  # padLen

        # m3p2Len，这部分等会再写
        buf_len = 64  
        self.m3p2Len = buf_len + 4 + 16
        options[4:6] = self.m3p2Len.to_bytes(2, 'big')

        # tsA
        seconds_since_epoch = int((time.time() * 1000 + 500) / 1000)
        options[8:12] = struct.pack('>I', seconds_since_epoch)
        # 初始化 12 字节的 nonce 数组，并将其设为零
        nonce = bytearray(12)

        # 创建 ChaCha20Poly1305 对象
        # key 密钥 m_CK + 32
        # ad 附加数据，用于验证但不加密 h: 32byte
        ad = self.h
        key = self.k
        msg = options
        chacha = ChaCha20Poly1305(key)

        # 加密
        encrypted_msg = chacha.encrypt(nonce, msg, ad)

        self.m_SessionRequestBuffer[32:64] = encrypted_msg

    # 用来验证SessionCreated是否符合NTCP2，从而判断Bob是否是i2p结点
    # data为sessioncreated
    def SessionConfirmed(self, data):
        if len(data) >= 64 and len(data) <= 287:
            # 假设的加密数据、密钥和 IV（您需要用实际的数据替换这些）
            self.KDF2Alice()
            encrypted_data = data[32:64]
            key = self.k
            chacha = ChaCha20Poly1305(key)
            nonce = b"\x00" * 12  # nonce的长度应该是12字节
            associated_data = self.h
            # 解密数据
            try:
                # 如果有附加数据，将其作为第二个参数传递
                decrypted_data = chacha.decrypt(nonce, encrypted_data, associated_data)
                print("解密后的数据:", decrypted_data)
                return True
            except Exception as e:
                print(f"解密错误: {e}")
                return False

        else:
            logger.error("data的长度与SessionCreated不符")
            return False
        

    def KDF1Alice(self):
        # Define protocol_name
        protocol_name = b"Noise_XKaesobfse+hs2+hs3_25519_ChaChaPoly_SHA256"
        # Define Hash h = 32 bytes
        self.h = hashlib.sha256(protocol_name).digest()
        # Define ck = 32 byte chaining key. Copy the h data to ck.
        self.ck = self.h

        # Define rs = Bob's 32-byte static key as published in the RouterInfo
        # This needs to be obtained from Bob's RouterInfo
        rs = self.m_remoteStaticKey  # Bob的公钥

        # MixHash(null prologue)
        self.h = hashlib.sha256(self.h).digest()

        # Bob static key
        # MixHash(rs)
        self.h = hashlib.sha256(self.h + rs).digest()



        # Alice ephemeral key X
        # MixHash(e.pubkey)

        self.h = hashlib.sha256(self.h + self.my_key.get_public_byte()).digest()

        # End of "e" message pattern.

        # "es" message pattern
        # DH(e, rs) == DH(s, re)
        # Assuming you have Bob's public key for DH
        bob_public_key = x25519.X25519PublicKey.from_public_bytes(self.m_remoteStaticKey)  # Bob's public key object of X25519

        # Define input_key_material = 32 byte DH result of Alice's ephemeral key and Bob's static key
        self.input_key_material = self.my_key.get_private().exchange(bob_public_key)

        # MixKey(DH())
        def hmac_sha256(key, data):
            return hmac.new(key, data, hashlib.sha256).digest()

        temp_key = hmac_sha256(self.ck, self.input_key_material)

        # Output 1
        self.ck = hmac_sha256(temp_key, b'\x01')

        # Output 2
        # Generate the cipher key k
        self.k = hmac_sha256(temp_key, self.ck + b'\x02')

        # End of "es" message pattern

    def KDF2Alice(self):
        self.h = hashlib.sha256(self.h + self.m_SessionRequestBuffer[:32]).digest()
        self.h = hashlib.sha256(self.h + self.m_SessionRequestBuffer[64:]).digest()
        self.h = hashlib.sha256(self.h + self.m_remoteStaticKey).digest()

        temp_key = hmac.new(self.ck, self.input_key_material, hashlib.sha256).digest()
        # 设置新的链接密钥
        ck = hmac.new(temp_key, b"\x01", hashlib.sha256).digest()

        # 生成加密密钥 k
        self.k = hmac.new(temp_key, ck + b"\x02", hashlib.sha256).digest()


class my_X25519():
    def __init__(self):
        # 生成一个新的 X25519 私钥
        self.private_key = x25519.X25519PrivateKey.generate()
        # 从私钥中导出公钥
        self.public_key = self.private_key.public_key()

    def get_public_byte(self):
        # 将公钥序列化为小端格式的字节
        ephemeral_key = self.public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        # 32字节，小端格式
        return ephemeral_key

    def get_public(self):
        return self.public_key
    
    def get_private(self):
        return self.private_key



if __name__ == "__main__":
    ntcp2 = NTCP2Establisher(os.urandom(32), os.urandom(16), os.urandom(32))
    ntcp2.CreateSessionRequestMessage()