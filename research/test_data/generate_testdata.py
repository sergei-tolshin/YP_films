import random

FIRST_PART = {
    "quantity": 10000000,
    "file_name": "first_part.csv",
    "first_part": True
}
SECOND_PART = {
    "quantity": 5000,
    "file_name": "second_part.txt",
    "first_part": False
}


def gen_data_part(quantity: int, file_name: str, first_part: bool) -> None:
    user_ids_range = (1, 10) if first_part else (5, 15)
    with open(file_name, "w") as file:
        if first_part:
            file.write("user_id,movie_id,viewed_frame\n")
        for _ in range(quantity):
            file.write(
                "id_{user},film_id_{film},{time}\n".format(
                    user=random.randint(user_ids_range[0], user_ids_range[1]),
                    film=random.randint(1, 100),
                    time=random.randint(1, 20000)
                )
            )


if __name__ == "__main__":
    gen_data_part(**FIRST_PART)
    gen_data_part(**SECOND_PART)
