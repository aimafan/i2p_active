# 在dell主机上运行，开多线程
import time
import socket
import os
import threading
import secrets
from utils import getconfig, getlog
from .connection import connect, logger
from .NTCP2 import NTCP2Establisher
import base64


config = getconfig.config

sole_host = config['solo']['host']
sole_port = int(config['solo']['port'])

def start_isi2p(ip_port, m_RemoteIdentHash, m_IV, m_remoteStaticKey):
    host = ip_port[0]
    port = ip_port[1]
    
    ntcp2 = NTCP2Establisher(m_RemoteIdentHash, m_IV, m_remoteStaticKey)
    ntcp2.CreateSessionRequestMessage()
    logger.info(f"Router Hash: {m_RemoteIdentHash}, IV: {m_IV}, remote static key: {m_remoteStaticKey}")
    logger.info(f"SessionRequestMessage: {ntcp2.m_SessionRequestBuffer}")
    data = connect(host, port, ntcp2.m_SessionRequestBuffer)
    if data != 0:
        return ntcp2.SessionConfirmed(data)
    else:
        return False

def base64replace(m_RemoteIdentHash, m_IV, m_remoteStaticKey):
    return base64.urlsafe_b64decode(m_RemoteIdentHash.replace('-', '+').replace('~', '/')), base64.urlsafe_b64decode(m_IV.replace('-', '+').replace('~', '/')), base64.urlsafe_b64decode(m_remoteStaticKey.replace('-', '+').replace('~', '/'))

if __name__=='__main__':
    host = "5.196.8.113"
    port = 32168

    # [ip, port], m_RemoteIdentHash, m_IV, m_remoteStaticKey
    # 32byte, 16byte, 32byte
    m_RemoteIdentHash = '6ivD02-G8AjzHelQkHIljB2pe9jHkZjFqgFXpSSLdOM='
    m_IV = 'uJJeAqdpwYWJ6tQBsFz6UQ=='
    m_remoteStaticKey = 'Pzu~0bCeFK7EhOB4tehUISEuzBYSC6XtEi7lFVdh-g8='
    m_RemoteIdentHash, m_IV, m_remoteStaticKey = base64replace(m_RemoteIdentHash, m_IV, m_remoteStaticKey)

    isi2p = start_isi2p([host, port], m_RemoteIdentHash, m_IV, m_remoteStaticKey)
    print(isi2p)