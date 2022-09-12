from logging import getLogger
from django.contrib.postgres.aggregates import ArrayAgg
from django.http import JsonResponse
from django.views.generic.list import BaseListView
from django.views.generic.detail import BaseDetailView
from django.db.models import Q

from movies import models

logger = getLogger(__name__)


class MoviesApiMixin:
    def get_queryset(self):
        filmworks = self.model.objects.values()
        filmworks = filmworks.annotate(genres=ArrayAgg('genres__name', distinct=True))
        for role_type in models.FilmworkRole:
            annotate_kwargs = {
                f'{role_type.value}s': ArrayAgg(
                    'persons__full_name',
                    filter=Q(filmworkperson__role=role_type),
                    distinct=True
                )
            }
            filmworks = filmworks.annotate(**annotate_kwargs)
        return filmworks.order_by('title')

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)


class MoviesListApi(MoviesApiMixin, BaseListView):
    model = models.Filmwork
    http_method_names = ['get']
    paginate_by = 50

    def get_context_data(self, **kwargs):
        queryset = self.get_queryset()
        page_number = self.request.GET.get('page') or 1
        paginator, page, queryset, _ = self.paginate_queryset(
            queryset,
            self.paginate_by
        )
        if page_number == 'last':
            page_number = paginator.num_pages
        paginator.page(page_number)
        context = {
            'count': paginator.count,
            'total_pages': paginator.num_pages,
            'next': page.next_page_number() if page.has_next() else None,
            'prev': page.previous_page_number() if page.has_previous() else None,
            'results': list(queryset)
        }
        return context


class MoviesDetailApi(MoviesApiMixin, BaseDetailView):
    model = models.Filmwork
    http_method_names = ['get']

    def get_context_data(self, **kwargs):
        return kwargs['object']
