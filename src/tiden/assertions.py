from .util import log_print


def tiden_assert(condition, text):
    log_print("Assert: {}".format(text), color='green' if condition else 'red')
    assert condition, text


def tiden_assert_is_none(value, text):
    is_none = value is None

    log_print("Assert: {} is None".format(text), color='green' if is_none else 'red')
    assert is_none, text


def tiden_assert_is_not_none(value, text):
    is_not_none = value is not None

    log_print("Assert: {} is not None".format(text), color='green' if is_not_none else 'red')
    assert is_not_none, text


def tiden_assert_equal(value_expected, actual_value, name):
    is_equal = actual_value == value_expected

    log_print("Assert '{}': {} == {}".format(name, value_expected, actual_value), color='green' if is_equal else 'red')
    assert is_equal, "Expected {} be equal to {}, got {}".format(name, value_expected, actual_value)


def tiden_assert_not_equal(value_expected, actual_value, name):
    is_not_equal = actual_value != value_expected

    log_print("Assert '{}': {} != {}".format(name, value_expected, actual_value),
              color='green' if is_not_equal else 'red')
    assert is_not_equal, "Expected {} be not equal to {}, got {}".format(name, value_expected, actual_value)
