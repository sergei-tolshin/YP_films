
import logging

from aioalice import Dispatcher, get_new_configured_app
from aioalice.dispatcher import MemoryStorage
from aiohttp import web
from pydantic import NoneIsAllowedError


from core.settings import WEBAPP_HOST, WEBAPP_PORT, WEBHOOK_URL_PATH
from core.utils import translate, get_lemma, get_obj_model_idx
from integrations.search import movie_search
from models.movie import Movie

logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] '
                    '#%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.INFO)

SEARCH_PARAM = {
    'рассказывать': lambda x: x.in_en.description,
    'сюжет': lambda x: x.in_en.description,
    'роль': lambda x: x.in_en.actors,
    'актер': lambda x: x.in_en.actors,
}


# Создаем экземпляр диспетчера и подключаем хранилище в памяти
dp = Dispatcher(storage=MemoryStorage())


# Новая сессия. Приветствуем пользователя
# В этот хэндлер будут попадать только новые сессии
@dp.request_handler(func=lambda areq: areq.session.new)
async def handle_new_session(alice_request):
    user_id = alice_request.session.user_id
    await dp.storage.update_data(
        user_id
    )
    logging.info(f'Initialized suggests for new session!\n'
                 f'user_id is {user_id!r}')
    return alice_request.response('Привет, я помощник в мире кино! '
                                  'Могу рассказать вам сюжет фильма, '
                                  'а также назвать актеров, сценаристов и '
                                  'режиссера. О каком фильме вам '
                                  'рассказать?')


@dp.request_handler()
async def handle_user_agrees(alice_request):
    lemmas = await get_lemma(alice_request)
    session = alice_request._raw_kwargs['state']['session']
    movie = ''
    search_param = 'фильм'
    if search_param not in lemmas and 'movie' in session and session['movie']:
        movie = Movie.parse_obj(session['movie'])
        for param in SEARCH_PARAM.keys():
            if param in lemmas:
                search_param = param
        return alice_request.response(
            SEARCH_PARAM[search_param](movie),
            session_state={
                "prev_movie_title": session['prev_movie_title'],
                "movie": movie.dict()
            }
        )

    movie_title = await get_obj_model_idx(lemmas, search_param)
    if movie_title is None:
        return alice_request.response(
            'Я вас не поняла',
            session_state={
                "prev_movie_title": movie_title,
                "movie": movie
            }
        )

    movie = await movie_search(movie_title)

    if movie is None:
        return alice_request.response(
            'Такого фильме нет',
            session_state={
                "prev_movie_title": movie_title,
                "movie": NoneIsAllowedError
            }
        )

    return alice_request.response(
        f'{movie.in_en.title}.\n',
        session_state={
            "prev_movie_title": movie_title,
            "movie": movie.dict()
            }
    )


# Все остальные запросы попадают в этот хэндлер,
# так как у него не настроены фильтры
@dp.request_handler()
async def handle_all_requests(alice_request):
    return alice_request.response(
        'Извините, не поняла вас. Повторите, пожалуйста, запрос.',
    )


@dp.errors_handler()
async def the_only_errors_handler(alice_request, error):
    logging.error('An error!', exc_info=error)
    if hasattr(error, 'assistant'):
        return alice_request.response(
            response_or_text=error.message
        )
    return alice_request.response(
        response_or_text=('Всё! Кина не будет! Электричество кончилось.\n'
                          'Скоро мы все починим.'),
        tts=('Всё! sil <[500]> Кин+а не будет! sil <[500]>'
             'Электр+ичество к+ончилось. sil <[1000]> Скоро мы все починим.')
    )


if __name__ == '__main__':
    app = get_new_configured_app(dispatcher=dp, path=WEBHOOK_URL_PATH)
    web.run_app(app, host=WEBAPP_HOST, port=WEBAPP_PORT)
