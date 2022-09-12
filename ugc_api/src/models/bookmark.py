from models.base import BaseOrJSONModel, MovieId


class BookmarkRequest(MovieId):
    pass


class UsersBookmarksResponse(BaseOrJSONModel):
    bookmarks: list
