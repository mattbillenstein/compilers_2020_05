import pytest


def assert_expectations(token_iterator, expected_output):
    output_iterator = iter(expected_output)

    try:
        data = next(token_iterator)
        while data:
            try:
                expected_type, expected_val = next(output_iterator)
            except StopIteration:
                pytest.fail("More tokens than expected values")
            assert data.type == expected_type
            if expected_val:
                assert data.value == expected_val

            data = next(token_iterator)
    except StopIteration:
        # tokens exhausted. We're good.
        pass
