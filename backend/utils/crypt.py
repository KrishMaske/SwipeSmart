from config.settings import fernet

def encrypt(plaintxt):
    return fernet.encrypt(plaintxt.encode()).decode()

def decrypt(plaintxt):
    return fernet.decrypt(plaintxt.encode()).decode()