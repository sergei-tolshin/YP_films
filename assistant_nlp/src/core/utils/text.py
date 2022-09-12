import urllib.request


def encode_uri(url: str):
    return urllib.request.quote(url, safe='~@#$&()*!+=:;,.?/\'')


def pluralize(value: int, arg: str):
    args = arg.split(',')
    number = abs(int(value))
    left_number = number % 10
    right_number = number % 100

    if (left_number == 1) and (right_number != 11):
        return args[0]
    elif (left_number >= 2) and (left_number <= 4) and (
            (right_number < 10) or (right_number >= 20)
    ):
        return args[1]
    return args[2]
