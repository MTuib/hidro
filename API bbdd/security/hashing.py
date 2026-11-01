from pwdlib import PasswordHash

#Configuraió del hasher de pwdlib, Argon2id per defecte
password_hash = PasswordHash.recommended()

def hash_password(password: str):
    return password_hash.hash(password)

def verify_password(password: str, hashed: str):
    return password_hash.verify(password, hashed)