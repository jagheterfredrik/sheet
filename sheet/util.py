def constant_time_compare(val1, val2):
    """Returns True if the two strings are equal, False otherwise.

    The time taken is independent of the number of characters that match.

    Taken from Django Source Code
    """
    if len(val1) != len(val2):
        return False
    result = 0
    for x, y in zip(val1, val2):
        result |= ord(x) ^ ord(y)
    return result == 0
