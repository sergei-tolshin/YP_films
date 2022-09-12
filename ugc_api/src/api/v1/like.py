from uuid import UUID

from core.services import check_token, get_mongo_client
from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.responses import JSONResponse
from models.like import LikeRequest, MoviesLikesResponse, UsersLikesResponse

router = APIRouter(prefix="/like", tags=["like"])


@router.post("/add")
async def add_like(request_data: LikeRequest,
                   auth_response=Depends(check_token),
                   mongo=Depends(get_mongo_client)):
    """function adds like to movie"""

    # checks user's token
    if not auth_response.username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token not valid."
        )

    name = auth_response.username

    coll = mongo.movies.likes
    movie = await coll.find_one({"movie_id": f"{request_data.movie_id}"})

    # if movie not in db
    if not movie:
        data_to_mongo = {"usernames": [name],
                         "movie_id": str(request_data.movie_id)}
        await coll.insert_one(data_to_mongo)
        return JSONResponse(
            status_code=200,
            content={"message": "like was added"}
        )

    usernames = movie["usernames"]

    # checks that user haven't set like to the movie yet
    if name in usernames:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already liked.")

    _id = movie["_id"]
    usernames.append(name)
    data_to_mongo = {"usernames": usernames,
                     "movie_id": str(request_data.movie_id)}

    await coll.replace_one({"_id": _id}, data_to_mongo)

    return JSONResponse(
        status_code=200,
        content={"message": "like was added"}
    )


@router.delete("/delete")
async def remove_like(request_data: LikeRequest,
                      auth_response=Depends(check_token),
                      mongo=Depends(get_mongo_client)):
    """function removes like"""

    # checks user's token
    if not auth_response.username:
        raise HTTPException(
            status_code=status.status.HTTP_403_FORBIDDEN,
            detail="Token not valid."
        )

    name = auth_response.username

    coll = mongo.movies.likes
    movie = await coll.find_one({"movie_id": f"{request_data.movie_id}"})

    try:
        _id = movie["_id"]
        usernames = movie["usernames"]
        usernames.remove(name)
        data_to_mongo = {"usernames": usernames,
                         "movie_id": str(request_data.movie_id)}

        await coll.replace_one({"_id": _id}, data_to_mongo)
        return JSONResponse(
            status_code=200,
            content={"message": "like was deleted"}
        )
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wrong movie_id or user haven't added like to this movie")


@router.get("/movies-likes/{film_id}", response_model=MoviesLikesResponse)
async def movies_likes(film_id: UUID,
                       auth_response=Depends(check_token),
                       mongo=Depends(get_mongo_client)):
    """function returns movie's likes"""

    # checks user's token
    if not auth_response.username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token not valid."
        )

    coll = mongo.movies.likes
    movie = await coll.find_one({"movie_id": f"{film_id}"})
    try:
        likes_amount = len(movie["usernames"])
        users = movie["usernames"]
        return MoviesLikesResponse(likes_amount=likes_amount, users=users)
    except TypeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wrong movie_id or movie hasn't likes"
        )


@router.get("/users-likes", response_model=UsersLikesResponse)
async def users_likes(auth_response=Depends(check_token),
                      mongo=Depends(get_mongo_client)):
    """function returns user's likes"""

    # checks user's token
    if not auth_response.username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token not valid."
        )

    name = auth_response.username
    coll = mongo.movies.likes
    movies = []
    async for document in coll.find({"usernames": name}):
        movies.append(document["movie_id"])

    return UsersLikesResponse(movies=movies)
