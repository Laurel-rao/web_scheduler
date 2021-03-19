import base64
import os
from cryptography.fernet import Fernet


def encrypt_p(password):
    f = Fernet('6kdOdkNNloW1zlgU7v9pZj1rmyfI3XOem7e7ML8Zu9A=')
    p1 = password.encode()
    token = f.encrypt(p1)
    p2 = token.decode()
    return p2


def decrypt_p(password):
    f = Fernet('6kdOdkNNloW1zlgU7v9pZj1rmyfI3XOem7e7ML8Zu9A=')
    p1 = password.encode()
    token = f.decrypt(p1)
    p2 = token.decode()
    return p2


if __name__ == '__main__':
    key = base64.urlsafe_b64encode(os.urandom(32))  # 生成key
    print(key)
