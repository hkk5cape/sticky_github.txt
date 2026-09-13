# Sticky Notes 


## Task  status
- Completed: expanded suite of 35 passing tests; passing live-server HTTP checks; source code and all three design diagrams packaged together.
- Pending: manual browser checks and public GitHub publication. See the documents below before submission.

## Requirements
Python 3.10 or later and pip. Django 5.2.x is specified in requirements.txt. Verification used Django 5.2.17.

## Windows PowerShell setup
Extract this project, then open a terminal in the folder containing manage.py:

```powershell
py -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe manage.py migrate
.\venv\Scripts\python.exe manage.py collectstatic --noinput
.\venv\Scripts\python.exe manage.py runserver
```

Open http://127.0.0.1:8000/ in your browser. Stop the server with Ctrl+C. These commands do not require activating the virtual environment.

## macOS / Linux setup
```bash
python3 -m venv venv
venv/bin/python -m pip install -r requirements.txt
venv/bin/python manage.py migrate
venv/bin/python manage.py collectstatic --noinput
venv/bin/python manage.py runserver
```

#Use the application
1. Select **New note**, enter a title and content, and save.
2. Select a note title to read its full content.
3. Select **Edit**, change the text, and save.
4. Select **Delete**, then confirm; **Keep note** cancels deletion.
5. Notes are stored in SQLite and remain after a server restart.

This is a local shared board without sign-in. The optional Django admin is available at /admin/ after running `python manage.py createsuperuser` with your environment's Python. Development settings are not a production deployment configuration.

## Verify and maintain
Use your environment's Python for each command:
```bash
python manage.py check
python manage.py test
python manage.py makemigrations --check --dry-run
python manage.py migrate
python manage.py collectstatic --noinput
```
After changing a model, run `python manage.py makemigrations` followed by `python manage.py migrate`. The initial migration is already included: a reviewer needs only `migrate` for a fresh database.

## Submission contents
- `sticky_notes/`: project settings, root URLs, WSGI and ASGI entry points.
- `notes/`: app configuration, model, form, CRUD views, URLs, admin, migration and tests.
- `templates/base.html`: shared layout.
- `notes/templates/notes/`: list, detail, form and delete confirmation pages.
- `notes/static/notes/css/style.css`: responsive local stylesheet.
- `docs/`: use case, sequence and class diagrams in browser-readable SVG, plus design explanation and verification record.

`STATIC_ROOT` is `staticfiles/`. `collectstatic` creates that directory; `runserver` serves app static assets with DEBUG enabled.

The submission excludes virtual environments, SQLite data, caches and collected static files. Source migration files must remain included; they recreate the database schema.

## References
- Django generic editing views: https://docs.djangoproject.com/en/5.2/ref/class-based-views/generic-editing/
- Model forms: https://docs.djangoproject.com/en/5.2/topics/forms/modelforms/
- Static files: https://docs.djangoproject.com/en/5.2/howto/static-files/


