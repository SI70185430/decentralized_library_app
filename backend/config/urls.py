"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from books import admin_views as book_admin_views

urlpatterns = [
    path(
        "admin/books/register/",
        admin.site.admin_view(book_admin_views.book_register),
        name="admin_books_register",
    ),
    path(
        "admin/books/isbn-lookup/",
        admin.site.admin_view(book_admin_views.isbn_lookup),
        name="admin_books_isbn_lookup",
    ),
    path("admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("api/auth/", include("accounts.urls")),
    path("api/books/", include("books.urls")),
    path("api/", include("lending.urls")),
]

# 書籍登録画面用のcssとjsを読み込むための設定
if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
