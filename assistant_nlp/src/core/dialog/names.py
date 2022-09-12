class SOURCES:
    ALICE = 'alice'
    MARUSYA = 'marusya'
    SBER = 'sber'
    unknown_source_error_message = ('Источник должен быть '
                                    '{"alice", "marusya", "sber"}')


class COMMANDS:
    EXIT = 'exit'


class RESPONSE_RESULT:
    NOT_FOUND = 'not found'
    UNKNOWN = 'unknown'


class REQUEST_TYPES:
    SIMPLE_UTTERANCE = 'SimpleUtterance'
    BUTTON_PRESSED = 'ButtonPressed'
