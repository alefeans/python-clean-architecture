import pytest

from app.infra.api.extensions import adapt_type_error


@pytest.mark.parametrize(
    "input, expected",
    [
        (
            "DTO.__init__() missing 1 required positional argument: 'name'",
            "missing 1 required field: 'name'",
        ),
        (
            "DTO.__init__() missing 2 required positional arguments: 'name' and 'age'",
            "missing 2 required fields: 'name' and 'age'",
        ),
        (
            "DTO.__init__() missing 3 required positional arguments: 'name', 'id' and 'age'",
            "missing 3 required fields: 'name', 'id' and 'age'",
        ),
    ],
)
def test_if_adapts_type_error_validation_message_properly(input, expected):
    assert adapt_type_error(input) == expected
