from core.dialog.names import COMMANDS


class Response:
    def __init__(
            self,
            text,
            suggests=None,
            commands=None,
            voice=None,
            links=None,
            image_id=None,
            image_url=None,
            sound_url=None,
            gallery=None,
            image=None,
            user_object=None,
            raw_response=None,
            confidence=0.5,
            label=None,
            handler=None,
            rich_text=None,
            show_item_meta=None,
            no_response=False,
            attachment_filename=None,
            extra_directives=None,
            should_listen=None,
    ):
        self.text = text
        self.suggests = suggests or []
        self.commands = commands or []
        self.voice = voice if voice is not None else text
        self.links = links or []
        self.updated_user_object = user_object
        self.confidence = confidence
        self.image_id = image_id
        self.image_url = image_url
        self.sound_url = sound_url
        self.gallery = gallery
        self.image = image
        self.raw_response = raw_response
        self.handler = handler
        self.label = label
        if rich_text:
            self.set_text(rich_text)
        self.show_item_meta = show_item_meta
        self.no_response = no_response
        self.attachment_filename = attachment_filename
        self.extra_directives = extra_directives
        self.should_listen = should_listen

    @property
    def user_object(self):
        return self.updated_user_object

    @property
    def has_exit_command(self) -> bool:
        return self.commands and COMMANDS.EXIT in self.commands
