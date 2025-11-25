"""URL configuration for todo_project project."""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("", include("todos.urls")),
    path("admin/", admin.site.urls),
]
