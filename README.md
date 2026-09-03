# athina-web

Web dashboard for the [Athina](https://github.com/athina-edu/athina) autograder. Provides a browser-based interface for managing courses, assignments, students, and grading — without touching the command line.

> **Note:** Most users install via the [one-click-run bundle](https://github.com/athina-edu/athina-one-click-run) which includes athina-web, the grading engine, and a MySQL database in Docker.

## Features

- **Course management**: Create courses, enroll students via email or bulk import
- **Assignment management**: Create assignments from Git template repos, configure grading options
- **Student dashboard**: View grades, test reports, plagiarism reports per student
- **AI Guidance**: View LLM-generated feedback for each student (when LLM is enabled)
- **Force Rerun**: Trigger re-grading for individual students from the browser
- **GitLab Issues output**: Grades posted as issues in each student's own GitLab repo
- **Faculty profiles**: Manage GitLab/GitHub credentials and LLM API keys per instructor
- **Role-based access**: Admin, Faculty, and Teaching Assistant roles with course-level permissions
- **File browser**: Browse and edit assignment files, test scripts, and configurations
- **GitLab webhooks**: Automatic re-grading when students push new commits

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│  athina-web │────▶│  MySQL DB    │◀────│  athina-cli  │
│  (Django)   │     │  (grades,    │     │  (grading    │
│  Port 8000  │     │   users)     │     │   daemon)    │
└─────────────┘     └──────────────┘     └──────┬───────┘
       │                                         │
       │  reads/writes                           │  clones repos
       │  assignment configs                     │  runs tests
       ▼                                         ▼
  .env files                            ┌──────────────┐
  (per assignment)                      │  Docker /    │
                                        │  firejail    │
                                        │  (sandbox)   │
                                        └──────────────┘
```

### Dual Database Architecture

1. **Django DB** (SQLite/MySQL): Assignment model, auth, sessions
2. **Grading DB** (MySQL): Student data, grades, test reports, LLM feedback — managed by `athina-cli`

The web app queries the grading DB directly via PyMySQL to display student results.

## Tech Stack

- **Backend**: Django 3.2 + Django REST Framework
- **Database**: SQLite (development) / MySQL 8.0 (production)
- **Auth**: Django built-in auth + django-registration
- **Frontend**: Bootstrap 4, jQuery, Font Awesome
- **Server**: Gunicorn (production) / Django dev server (development)

## Quick Start

### Development

```bash
# Install dependencies
pip install -e .

# Set up database
python manage.py migrate
python manage.py createsuperuser

# Run development server
python manage.py runserver 0.0.0.0:8000
```

### Docker

```bash
docker-compose up
```

## Configuration

### Settings

Copy `athinaweb/settings_secret.py.template` to `athinaweb/settings_secret.py` and configure:

```python
SECRET_KEY = '<your-secret-key>'
DATABASES = { ... }
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ATHINA_MYSQL_HOST` | `localhost` | Grading database host |
| `ATHINA_MYSQL_PORT` | `3306` | Grading database port |
| `ATHINA_MYSQL_USERNAME` | `athina` | Grading database user |
| `ATHINA_MYSQL_PASSWORD` | — | Grading database password |

### Per-Assignment `.env` Files

Each assignment directory contains an auto-generated `.env` file with credentials for the grading engine. These are written automatically when a faculty member saves their profile or creates an assignment.

```
GIT_PROVIDER=gitlab
GIT_URL=gitlab.cs.wwu.edu
GIT_USERNAME=faculty_user
GIT_PASSWORD=<access-token>
LLM_ENDPOINT_URL=https://api.openai.com/v1
LLM_API_KEY=<api-key>
LLM_MODEL=gpt-4o
OUTPUT_METHOD=gitlab_issues
```

## URL Routes

| Path | Description |
|------|-------------|
| `/` | Home / course list |
| `/assignments/courses/` | Course management |
| `/assignments/<id>/` | Assignment student view |
| `/assignments/<id>/report/<uid>/test` | Student test report |
| `/assignments/<id>/report/<uid>/plagiarism` | Student plagiarism report |
| `/assignments/<id>/guidance/<uid>` | AI guidance (JSON API) |
| `/assignments/<id>/force/<uid>` | Force re-grading |
| `/filemanager/` | Assignment file browser |
| `/admin/` | Django admin |
| `/accounts/login/` | Login |
| `/accounts/profile/` | Faculty profile (credentials) |

## Deployment

See [athina-one-click-run](https://github.com/athina-edu/athina-one-click-run) for a production-ready Docker Compose setup with nginx, MySQL, and SSL.

## License

MIT
