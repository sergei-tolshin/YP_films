from uuid import UUID

from core.services import check_token, get_mongo_client
from fastapi import APIRouter, status, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from models.review import ReviewRequest, MoviesReviewsResponse, UsersReviewsResponse

from models.base import MovieId

router = APIRouter(prefix="/review", tags=["review"])


@router.post("/add")
async def add_review(request_data: ReviewRequest,
                     auth_response=Depends(check_token),
                     mongo=Depends(get_mongo_client)):
    """function adds review to movie"""

    if not auth_response.username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token not valid."
        )

    name = auth_response.username

    coll = mongo.movies.reviews
    movie = await coll.find_one({"movie_id": f"{request_data.movie_id}"})
    if not movie:
        data_to_mongo = {'movie_id': str(request_data.movie_id),
                         'reviews': {name: request_data.review}}
        await coll.insert_one(data_to_mongo)

        return JSONResponse(
            status_code=200,
            content={"message": "review was added"}
        )

    reviews = movie["reviews"]
    if name in reviews:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User can post only one review to the same movie"
        )

    _id = movie["_id"]
    reviews[name] = request_data.review
    data_to_mongo = {"movie_id": str(request_data.movie_id),
                     "reviews": reviews}
    await coll.replace_one({'_id': _id}, data_to_mongo)

    return JSONResponse(
        status_code=200,
        content={"message": "review was added"}
    )


@router.delete("/delete")
async def delete_review(request_data: MovieId,
                        auth_response=Depends(check_token),
                        mongo=Depends(get_mongo_client)):
    """function delete review from movie"""

    if not auth_response.username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token not valid."
        )

    name = auth_response.username

    coll = mongo.movies.reviews
    movie = await coll.find_one({"movie_id": f"{request_data.movie_id}"})

    try:
        _id = movie["_id"]
        reviews = movie["reviews"]
        reviews.pop(name)
        data_to_mongo = {"movie_id": str(request_data.movie_id)}
        await coll.replace_one({'_id': _id}, data_to_mongo)

        return JSONResponse(
            status_code=200,
            content={"message": "review was deleted"}
        )

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wrong movie_id or user haven't written review to this movie yet"
        )


@router.get("/movies-reviews/{film_id}", response_model=MoviesReviewsResponse)
async def movies_reviews(film_id: UUID,
                         auth_response=Depends(check_token),
                         mongo=Depends(get_mongo_client)):
    """function returns all reviews of movie"""

    if not auth_response.username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token not valid."
        )

    coll = mongo.movies.reviews
    movie = await coll.find_one({"movie_id": f"{film_id}"})

    try:
        movie_id = movie["movie_id"]
        reviews = movie["reviews"]
        return MoviesReviewsResponse(movie_id=movie_id, reviews=reviews)

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wrong movie_id or movie haven't any reviews"
        )


@router.get("/users-reviews")
async def users_reviews(page_num: int = Query(default=1, ge=1),
                        page_size: int = Query(default=5, ge=1),
                        auth_response=Depends(check_token),
                        mongo=Depends(get_mongo_client)):
    """function returns all user's reviews"""

    if not auth_response.username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token not valid."
        )
    skips = page_size * (page_num - 1)
    name = auth_response.username
    coll = mongo.movies.reviews
    reviews = dict()
    async for document in coll.find({f"reviews.{name}": {"$exists": True}}).skip(skips).limit(page_size):
        reviews[document["movie_id"]] = document["reviews"][name]

    return UsersReviewsResponse(reviews=reviews)
