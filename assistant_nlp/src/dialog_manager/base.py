from core.dialog import Context, Response


class BaseDialogManager:
    def __init__(self, default_message: str = 'Это базовый диалог.'):
        self.default_message = default_message

    def respond(self, ctx: Context):
        return Response(text=self.default_message)
