from utils import password


def test_verify_hash():
    pwd_context = password.pwd_context
    test_password = "super-secure_pa$$word"
    hashed_password = pwd_context.hash(test_password)
    assert password.verify_hash(test_password, hashed_password)


def test_hash_password():
    pwd_context = password.pwd_context
    test_password = "super-secure_pa$$word"
    hashed_password = password.get_hash(test_password)
    pwd_context.verify(test_password, hashed_password)
