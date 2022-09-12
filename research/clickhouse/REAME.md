# Без параллельной загрузки данных
- Загрузка кусками по 100.000 записей занимает ~26 секунд
- Загрузка 10.000.000 записей занимает ~17 секунд, но при этом оперативная память потребляет больше 5Гб
- Загрузку кусочками (100 и 1000) нет особого смысла делать в силу долгого распределения в базе по партишену

```
SELECT count() FROM default.test - 0.0018
SELECT uniqExact(movie_id) FROM default.test - 0.4338
SELECT uniqExact(user_id) FROM default.test - 0.4411
SELECT user_id, uniqExact(movie_id) FROM default.test GROUP by user_id - 0.5922
SELECT user_id, sum(viewed_frame), max(viewed_frame) FROM default.test WHERE user_id='id_5' GROUP by user_id - 0.2834
SELECT user_id, sum(viewed_frame), max(viewed_frame) FROM default.test GROUP by user_id - 0.2925
```


# С параллельной загрузкой данных
- Загрузка кусками по 100.000 записей занимает ~26-40 секунд (зависит от количества записей в бд)
- Чем больше записей в БД тем дольше выполняются запросы по типу поиска уникального user_id
```
SELECT count() FROM default.test - 0.0229
SELECT uniqExact(movie_id) FROM default.test - 1.5332
SELECT uniqExact(user_id) FROM default.test - 1.3388
SELECT user_id, uniqExact(movie_id) FROM default.test GROUP by user_id - 2.4496
SELECT user_id, sum(viewed_frame), max(viewed_frame) FROM default.test WHERE user_id='id_5' GROUP by user_id - 1.267
SELECT user_id, sum(viewed_frame), max(viewed_frame) FROM default.test GROUP by user_id - 1.1722
```