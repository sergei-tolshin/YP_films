from uuid import uuid4
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from psqlextra.indexes import UniqueIndex


class TimeStampedModel(models.Model):
    id = models.UUIDField(primary_key=True, db_column='id', default=uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Genre(TimeStampedModel):
    name = models.CharField(_('title'), max_length=255)
    description = models.TextField(_('description'), blank=True, null=True)

    class Meta:
        verbose_name = _('genre')
        verbose_name_plural = _('genres')

        db_table = "content\".\"genre"

    def __str__(self):
        return str(self.name)


class FilmworkGenre(models.Model):
    id = models.UUIDField(primary_key=True, db_column='id', default=uuid4)
    filmwork = models.ForeignKey('Filmwork', on_delete=models.CASCADE, db_column='film_work_id')
    genre = models.ForeignKey('Genre', on_delete=models.CASCADE, db_column='genre_id')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "content\".\"genre_film_work"
        indexes = [
            UniqueIndex(
                fields=['filmwork', 'genre'],
                name='film_work_genre'
            )
        ]


class FilmworkType(models.TextChoices):
    MOVIE = 'movie', _('movie')
    TV_SHOW = 'tv_show', _('TV Show')


class FilmworkRole(models.TextChoices):
    ACTOR = 'actor', _('actor')
    DIRECTOR = 'director', _('director')
    WRITER = 'writer', _('writer')


class Person(TimeStampedModel):
    full_name = models.CharField(_('full name'), max_length=255)
    birth_date = models.DateField(_('birth date'), null=True)

    class Meta:
        verbose_name = _("person")
        verbose_name_plural = _("persons")

        db_table = "content\".\"person"

    def __str__(self):
        return str(self.full_name)


class FilmworkPerson(models.Model):
    id = models.UUIDField(primary_key=True, db_column='id', default=uuid4)
    filmwork = models.ForeignKey('Filmwork', on_delete=models.CASCADE, db_column="film_work_id")
    person = models.ForeignKey('Person', on_delete=models.CASCADE, db_column="person_id")
    role = models.CharField(_('role'), max_length=20, choices=FilmworkRole.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "content\".\"person_film_work"
        indexes = [
            UniqueIndex(
                fields=['filmwork', 'person', 'role'],
                name='film_work_person_role'

            )

        ]


class Filmwork(TimeStampedModel):
    title = models.CharField(_('title'), max_length=255)
    description = models.TextField(_('description'), blank=True, null=True)
    creation_date = models.DateField(_('creation date'), blank=True, null=True)
    certificate = models.TextField(_('certificate'), blank=True, null=True)
    file_path = models.FileField(_('file'), upload_to='film_works/', blank=True, null=True)
    rating = models.FloatField(
        _('rating'),
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        blank=True,
        null=True
    )
    type = models.CharField(_('type'), max_length=20, choices=FilmworkType.choices)
    genres = models.ManyToManyField(Genre, through='FilmworkGenre')
    persons = models.ManyToManyField(Person, through='FilmworkPerson')

    class Meta:
        verbose_name = _('filmwork')
        verbose_name_plural = _('filmworks')
        db_table = "content\".\"film_work"

    def __str__(self):
        return str(self.title)
