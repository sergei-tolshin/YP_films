from models.base import BaseOrJSONModel, MovieId


class ReviewRequest(MovieId):
    review: str


class MovieIdWIthToken(MovieId):
    pass


class UsersReview(BaseOrJSONModel):
    user_name: str
    review: str


class MoviesReviewsResponse(BaseOrJSONModel):
    movie_id: str
    reviews: dict[str, str]


class UsersReviewsResponse(BaseOrJSONModel):
    reviews: dict[str, str]
