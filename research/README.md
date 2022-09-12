# UGC спринт 1

## Исследование ClickHouse

### Без параллельной загрузки данных
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


### С параллельной загрузкой данных
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

## Исследование Vertica


### Результаты.

```
* Average time single query to database without load new data - 0.2699.
* Average time first query process to database with load new data - 0.3959.
* Average time second query process to database with load new data - 0.3999.
* Average time query batching load new data ( with chunk value 1000 ). - 7.4544.
```
- Среднее время получения данных без загрузки новых - 0.27.
- Среднее время получения данных с загрузкой новых - 0.4.
- Среднее время загрузки 1000 новых записей - 7.5.

## Выводы:
```
Для хранения данных аналитики просмотров целособразнее использовать ClickHouse,
т. к. в бесплатном варианте результаты лучше. А денег нет :(
```

_______________________________________________________________________________________

# UGC спринт 2

## Исследование MongoDb

### Результат исследования

| Название теста                   | Минимальное значение | Максимальное значение | Среднее значение | Количество повторений | 
|----------------------------------|----------------------|-----------------------|------------------|-----------------------| 
| Test select_review               | 0.00099         | 0.00415          | 0.00197 | 10                    |
| Test select_user_bookmarks       | 0.00116         | 0.00162          | 0.00134 | 10                    |
| Test select_movie_likes          | 0.00103         | 0.00181          | 0.00155 | 10                    |
| Test select_coun_movie_likes     | 0.00128         | 0.00218          | 0.00168 | 10                    |
| Test add_like_movie              | 0.00724         | 0.01460          | 0.01039 | 10                    |
| Test add_review                  | 0.00442         | 0.00849          | 0.00541 | 10                    |
| Test add_like_review             | 0.00724         | 0.02194          | 0.01135 | 10                    |
| Test add_bookmarks               | 0.00338         | 0.00748          | 0.00441 | 10                    |


## Выводы:

    Система удовлетворяет требованиям
