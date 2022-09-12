# Generated by Django 3.2.9 on 2021-11-25 20:55

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import psqlextra.indexes.unique_index
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.RunSQL("CREATE SCHEMA content;", "DROP SCHEMA content;"),

        migrations.CreateModel(
            name='Filmwork',
            fields=[
                ('id', models.UUIDField(db_column='id', default=uuid.uuid4, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=255, verbose_name='title')),
                ('description', models.TextField(blank=True, null=True, verbose_name='description')),
                ('creation_date', models.DateField(blank=True, null=True, verbose_name='creation date')),
                ('certificate', models.TextField(blank=True, null=True, verbose_name='certificate')),
                ('file_path', models.FileField(blank=True, null=True, upload_to='film_works/', verbose_name='file')),
                ('rating', models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(10)], verbose_name='rating')),
                ('type', models.CharField(choices=[('movie', 'movie'), ('tv_show', 'TV Show')], max_length=20, verbose_name='type')),
            ],
            options={
                'verbose_name': 'filmwork',
                'verbose_name_plural': 'filmworks',
                'db_table': 'content"."film_work',
            },
        ),
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('id', models.UUIDField(db_column='id', default=uuid.uuid4, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255, verbose_name='title')),
                ('description', models.TextField(blank=True, null=True, verbose_name='description')),
            ],
            options={
                'verbose_name': 'genre',
                'verbose_name_plural': 'genres',
                'db_table': 'content"."genre',
            },
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.UUIDField(db_column='id', default=uuid.uuid4, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('full_name', models.CharField(max_length=255, verbose_name='full name')),
                ('birth_date', models.DateField(null=True, verbose_name='birth date')),
            ],
            options={
                'verbose_name': 'person',
                'verbose_name_plural': 'persons',
                'db_table': 'content"."person',
            },
        ),
        migrations.CreateModel(
            name='FilmworkPerson',
            fields=[
                ('id', models.UUIDField(db_column='id', default=uuid.uuid4, primary_key=True, serialize=False)),
                ('role', models.CharField(choices=[('actor', 'actor'), ('director', 'director'), ('writer', 'writer')], max_length=20, verbose_name='role')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('filmwork', models.ForeignKey(db_column='film_work_id', on_delete=django.db.models.deletion.CASCADE, to='movies.filmwork')),
                ('person', models.ForeignKey(db_column='person_id', on_delete=django.db.models.deletion.CASCADE, to='movies.person')),
            ],
            options={
                'db_table': 'content"."person_film_work',
            },
        ),
        migrations.CreateModel(
            name='FilmworkGenre',
            fields=[
                ('id', models.UUIDField(db_column='id', default=uuid.uuid4, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('filmwork', models.ForeignKey(db_column='film_work_id', on_delete=django.db.models.deletion.CASCADE, to='movies.filmwork')),
                ('genre', models.ForeignKey(db_column='genre_id', on_delete=django.db.models.deletion.CASCADE, to='movies.genre')),
            ],
            options={
                'db_table': 'content"."genre_film_work',
            },
        ),
        migrations.AddField(
            model_name='filmwork',
            name='genres',
            field=models.ManyToManyField(through='movies.FilmworkGenre', to='movies.Genre'),
        ),
        migrations.AddField(
            model_name='filmwork',
            name='persons',
            field=models.ManyToManyField(through='movies.FilmworkPerson', to='movies.Person'),
        ),
        migrations.AddIndex(
            model_name='filmworkperson',
            index=psqlextra.indexes.unique_index.UniqueIndex(fields=['filmwork', 'person', 'role'], name='film_work_person_role'),
        ),
        migrations.AddIndex(
            model_name='filmworkgenre',
            index=psqlextra.indexes.unique_index.UniqueIndex(fields=['filmwork', 'genre'], name='film_work_genre'),
        ),
    ]