from models.base import BaseOrJSONModel, MovieId


class LikeRequest(MovieId):
    pass


class MoviesLikesResponse(BaseOrJSONModel):
    likes_amount: int
    users: list


class UsersLikesResponse(BaseOrJSONModel):
    movies: list
