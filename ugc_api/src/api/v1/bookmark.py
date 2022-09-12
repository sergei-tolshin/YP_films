from core.services import check_token, get_mongo_client, add_extra_fields_in_logger_record
from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.responses import JSONResponse
from models.bookmark import BookmarkRequest, UsersBookmarksResponse

router = APIRouter(prefix="/bookmark", tags=["bookmark"])


@router.post("/add")
async def add_bookmarks(request_data: BookmarkRequest,
                        auth_response=Depends(check_token),
                        mongo=Depends(get_mongo_client),
                        logger_=Depends(add_extra_fields_in_logger_record)):
    """function adds movie to user's bookmarks"""

    if not auth_response.username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token not valid."
        )

    name = auth_response.username
    logger_.info("Get username - " + str(name))
    coll = mongo.movies.bookmarks
    user = await coll.find_one({"user_name": name})

    if not user:
        data_to_mongo = {"user_name": name,
                         "bookmarks": [str(request_data.movie_id)]}

        await coll.insert_one(data_to_mongo)
        return JSONResponse(
            status_code=200,
            content={"message": "bookmark was added"}
        )

    bookmarks = user["bookmarks"]
    if str(request_data.movie_id) in bookmarks:
        logger_.info("Entry already created.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="movie already in bookmarks")

    _id = user["_id"]
    bookmarks.append(str(request_data.movie_id))
    data_to_mongo = {"user_name": name,
                     "bookmarks": bookmarks}
    await coll.replace_one({"_id": _id}, data_to_mongo)

    return JSONResponse(
        status_code=200,
        content={"message": "bookmark was added"}
    )


@router.get("/get", response_model=UsersBookmarksResponse)
async def get_users_bookmarks(auth_response=Depends(check_token),
                              mongo=Depends(get_mongo_client)):
    """function returns users bookmarks"""

    if not auth_response.username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token not valid."
        )

    name = auth_response.username

    coll = mongo.movies.bookmarks
    user = await coll.find_one({"user_name": name})
    bookmarks = user["bookmarks"]

    return UsersBookmarksResponse(bookmarks=bookmarks)


@router.delete("/delete")
async def delete_bookmark(request_data: BookmarkRequest,
                          auth_response=Depends(check_token),
                          mongo=Depends(get_mongo_client)):
    """function removes movie from user's bookmarks"""

    if not auth_response.username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token not valid."
        )

    name = auth_response.username

    coll = mongo.movies.bookmarks
    user = await coll.find_one({"user_name": name})
    bookmarks = user["bookmarks"]

    try:
        _id = user["_id"]
        bookmarks.remove(str(request_data.movie_id))
        data_to_mongo = {"user_name": name,
                         "bookmarks": bookmarks}
        await coll.replace_one({"_id": _id}, data_to_mongo)

        return JSONResponse(
            status_code=200,
            content={"message": "bookmark was deleted"}
        )

    except ValueError:
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wrong movie_id"
        )
