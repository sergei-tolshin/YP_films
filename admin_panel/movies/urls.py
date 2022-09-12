from django.urls import path, include


urlpatterns = [
    path('api/', include('movies.api.urls')),
]
