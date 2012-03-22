def computeLRC(data):
    ''' Wrapper to computer LRC of multiple types of data

    .. note:: This accepts a string or a integer list

    example::

        return computeLRC(input) == 2

    :param data: The data to apply a lrc to

    '''
    if isinstance(data, str): data = ascii2hex(data)

    lrc = sum(data)
    return 0x100 - lrc

def checkLRC(data, check):
    ''' Checks if the passed in data matches the LRC

    example::

        return checkLRC(input, 2)

    :param data: The data to calculate
    :param check: The LRC to validate
    '''
    return computeLRC(data) == check

def a2h(a):
    '''
    Converts ascii chars to hex values:

        "0" -> 0
        "1" -> 1
        "f" -> 15
        "F" -> 15

    :param a: the char to be converted
    '''
    o = ord(a)
    if 47 < o < 58:
        return ord(a) - 48
    else:
        A = a.upper()
        O = ord(A)
        if 64 < O < 71:
            return O - 55
        else:
            raise ValueError("ASCII value out of hex range: %s %s %d %d" % (a, A,O, o))

def ascii2hex(buffer):
    '''
    Take chars by pairs and create an hex value from them.
    Return a list with the resulting values.
    Used to decode Modbus ASCII packets.

    :param buffer: the string from an ascii modbus device
                   without ':' and '\\r\\n'
    :return a list of values.
    '''
    i = iter(buffer)
    out = []
    for x, y in zip(i, i):
        x, y = a2h(x), a2h(y)
        out.append(x << 4 | y)
    return out