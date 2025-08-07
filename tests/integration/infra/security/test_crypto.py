from app.infra.security.crypto import Hasher


def test_if_hashes_value():
    hasher = Hasher()
    value = "testing"
    assert value != hasher.hash(value)


def test_if_returns_true_when_checking_hashed_value():
    hasher = Hasher()
    value = "testing"
    hashed = hasher.hash(value)
    assert hasher.verify(value, hashed)


def test_if_returns_false_when_hashed_value_is_different():
    hasher = Hasher()
    value = "testing"
    hashed = hasher.hash("different")
    assert not hasher.verify(value, hashed)
