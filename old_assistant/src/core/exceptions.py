class AssistantException(Exception):
    def __init__(self, message):
        self.assistant = True
        self.message = message
        super().__init__(self.message)


class MovieNotFoundException(AssistantException):
    def __init__(
        self,
        message: str = 'Похоже такой фильм еще не сняли, назовите другой!'
    ):
        self.message = message
        super().__init__(self.message)
