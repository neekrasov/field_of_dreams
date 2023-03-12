from hashlib import sha256


class PasswordHasher:
    def __init__(self, salt: str):
        self.salt = salt

    def hash(self, password: str) -> str:
        return sha256(password.encode()).hexdigest()

    def verify(self, password: str, hashed: str) -> bool:
        return self.hash(password) == hashed
