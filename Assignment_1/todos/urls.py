from django.urls import path

from . import views

app_name = "todos"

urlpatterns = [
    path("", views.list_todos, name="list"),
    path("create/", views.create_todo, name="create"),
    path("<int:pk>/edit/", views.edit_todo, name="edit"),
    path("<int:pk>/delete/", views.delete_todo, name="delete"),
    path("<int:pk>/toggle/", views.toggle_completion, name="toggle"),
]
