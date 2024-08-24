import hashlib
from dotenv import dotenv_values

config = dotenv_values(".env")

def hash_password(password):
    """Gera um hash SHA-256 da senha."""
    salt = config['PSSWD_SALT'].split(',')
    password = salt[0] + password + salt[1]
    return hashlib.sha256(password.encode()).hexdigest()