from django.urls import path

from . import views

app_name = "books"

urlpatterns = [
    path("", views.BookListView.as_view(), name="book-list"),
    path("genres/", views.GenreListView.as_view(), name="genre-list"),
    path("<uuid:pk>/", views.BookDetailView.as_view(), name="book-detail"),
]
