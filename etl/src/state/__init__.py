from .state import init_state, State
from .storage import MIN_TIMESTAMP

FILM_STATE = init_state('film')
GENRE_STATE = init_state('genre')
PERSON_STATE = init_state('person')

STATES = (FILM_STATE, GENRE_STATE, PERSON_STATE)
