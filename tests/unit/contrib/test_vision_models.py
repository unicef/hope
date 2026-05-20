from hope.contrib.vision.models import FundsCommitment


def test_funds_commitment_str_returns_funds_commitment_number():
    fc = FundsCommitment(rec_serial_number=1, funds_commitment_number="FC123")

    assert str(fc) == "FC123"


def test_funds_commitment_str_returns_empty_string_when_number_is_none():
    fc = FundsCommitment(rec_serial_number=2, funds_commitment_number=None)

    assert str(fc) == ""
