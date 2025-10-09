# ==== backend/utils/auth_utils.py ====
from passlib.context import CryptContext

# Use a pure-Python, widely available hashing scheme to avoid native bcrypt backend issues
# pbkdf2_sha256 is strong and avoids platform-specific wheels
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain-text password against a hashed password.
    
    Args:
        plain_password (str): The password provided by the user.
        hashed_password (str): The stored hashed password.
        
    Returns:
        bool: True if passwords match, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Hashes a plain-text password.
    
    Args:
        password (str): The plain-text password to hash.
        
    Returns:
        str: The hashed password.
    """
    return pwd_context.hash(password)

# Example Usage (for testing/debugging)
if __name__ == "__main__":
    test_password = "mySecretPassword123"
    hashed_p = get_password_hash(test_password)
    print(f"Original password: {test_password}")
    print(f"Hashed password: {hashed_p}")

    assert verify_password(test_password, hashed_p) == True
    print(f"Verification with correct password successful: {verify_password(test_password, hashed_p)}")

    assert verify_password("wrong_password", hashed_p) == False
    print(f"Verification with incorrect password successful: {verify_password('wrong_password', hashed_p)}")