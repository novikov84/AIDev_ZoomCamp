# Assignment_1: Django TODO app

Simple Django-based TODO manager with due dates and completion toggle.

## Setup
1) Create env (conda example): `conda create -n django python=3.11 django`
2) Activate: `conda activate django`
3) From `Assignment_1/`:
   - Run migrations: `python manage.py migrate`
   - Start server: `python manage.py runserver`

## Features
- Create, edit, delete TODOs
- Due dates and completion toggle
- Basic styling and admin registration

## Tests
- Run: `python manage.py test`

## Screenshot
![Django TODOs](assets/todo-screenshot.png)
