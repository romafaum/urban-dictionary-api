from django.urls import path
from main.views import definitions_view, author_view, random_view

urlpatterns = [
    path('author/<str:name>/', author_view, name='author'),
    path('definitions/<str:name>/', definitions_view, name='definitions'),
    path('random', random_view, name='random'),
]