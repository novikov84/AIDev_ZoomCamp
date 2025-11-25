from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import TodoForm
from .models import Todo


def list_todos(request):
    todos = Todo.objects.all()
    return render(request, "todos/todo_list.html", {"todos": todos})


def create_todo(request):
    if request.method == "POST":
        form = TodoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("todos:list")
    else:
        form = TodoForm()

    return render(
        request,
        "todos/todo_form.html",
        {"form": form, "heading": "Create TODO", "submit_label": "Create"},
    )


def edit_todo(request, pk):
    todo = get_object_or_404(Todo, pk=pk)
    if request.method == "POST":
        form = TodoForm(request.POST, instance=todo)
        if form.is_valid():
            form.save()
            return redirect("todos:list")
    else:
        form = TodoForm(instance=todo)

    return render(
        request,
        "todos/todo_form.html",
        {"form": form, "heading": "Edit TODO", "submit_label": "Save"},
    )


def delete_todo(request, pk):
    todo = get_object_or_404(Todo, pk=pk)
    if request.method == "POST":
        todo.delete()
        return redirect("todos:list")

    return render(request, "todos/confirm_delete.html", {"todo": todo})


def toggle_completion(request, pk):
    todo = get_object_or_404(Todo, pk=pk)
    todo.completed = not todo.completed
    todo.save(update_fields=["completed"])
    return redirect(request.GET.get("next") or reverse("todos:list"))
