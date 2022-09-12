from django.contrib import admin
from .models import Filmwork, Genre, Person


class GenreInlineAdmin(admin.TabularInline):
    model = Filmwork.genres.through
    fields = ('genre', )
    extra = 0


class PersonInlineAdmin(admin.TabularInline):
    model = Filmwork.persons.through
    fields = ('person', 'role')
    extra = 0


@admin.register(Filmwork)
class FilmworkAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'creation_date', 'rating',)
    list_filter = ("type", 'genres')
    search_fields = ('title', 'description', 'id')
    fields = (
        'title', 'type', 'description', 'creation_date', 'certificate',
        'file_path', 'rating',
    )

    inlines = (GenreInlineAdmin, PersonInlineAdmin)
    list_prefetch_relateda = ['genres', 'persons']


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    fields = ('name', 'description')
    search_fields = ('name', 'description', 'id')


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    fields = ('full_name', 'birth_date')
    search_fields = ('full_name', 'birth_date', 'id')
