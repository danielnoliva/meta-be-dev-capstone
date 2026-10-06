# Little Lemon backend

A Django REST API for the Little Lemon restaurant, built for the Meta Back-End Developer Capstone. It includes a restaurant homepage, menu management, table bookings, user registration, token authentication, and the Django admin interface.

The project uses Python 3.13+, Django, Django REST Framework, Djoser, and MySQL. Dependency versions are recorded in `uv.lock`.

## Get started

Run the commands below from the project root (the directory containing `manage.py`). Shell examples use macOS/Linux syntax; on Windows, use WSL for the same commands.

### 1. Install prerequisites

You need Git, Python 3.13 or newer, [uv](https://docs.astral.sh/uv/), and a running MySQL server. The `mysqlclient` Python package also needs MySQL development libraries and build tools.

On macOS with Homebrew:

```bash
brew install python@3.13 uv mysql pkg-config
brew services start mysql
```

On Ubuntu/Debian, install the MySQL server and native build dependencies:

```bash
sudo apt update
sudo apt install mysql-server default-libmysqlclient-dev build-essential pkg-config python3-dev
sudo service mysql start
```

Install uv if it is not already available, then let it install the project's Python version:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
# Open a new terminal if uv is not yet on PATH.
uv python install 3.13
```

If `mysqlclient` cannot find Python headers during installation, install the development headers matching the Python interpreter you use.

### 2. Get the project and install dependencies

Clone your copy of this repository, replacing `<repository-url>` with its Git URL:

```bash
git clone <repository-url> meta-be-dev-capstone
cd meta-be-dev-capstone
uv sync --locked
```

If you already have the repository, change into its directory and run `uv sync --locked`. This creates a local `.venv` and installs the locked dependencies. Commands below use `uv run`, so activating the virtual environment is unnecessary.

### 3. Create the MySQL database and user

Connect as a MySQL administrator:

```bash
mysql -u root -p
```

On Ubuntu installations using socket authentication, use `sudo mysql` instead. Run this SQL, replacing the example password with your own local password:

```sql
CREATE DATABASE littlelemon CHARACTER SET utf8mb4;
CREATE USER 'littlelemon'@'127.0.0.1' IDENTIFIED BY 'replace-with-your-local-password';
GRANT ALL PRIVILEGES ON littlelemon.* TO 'littlelemon'@'127.0.0.1';
EXIT;
```

### 4. Configure the database connection

The settings read these environment variables:

| Variable | Default | Meaning |
| --- | --- | --- |
| `MYSQL_DATABASE` | `littlelemon` | Database name |
| `MYSQL_USER` | `root` | MySQL account |
| `MYSQL_PASSWORD` | Empty string | MySQL password |
| `MYSQL_HOST` | `127.0.0.1` | MySQL server address |
| `MYSQL_PORT` | `3306` | MySQL server port |

Create a `.env` file in the project root with the credentials from step 3:

```bash
MYSQL_DATABASE=littlelemon
MYSQL_USER=littlelemon
MYSQL_PASSWORD='replace-with-your-local-password'
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
```

**The application does not load `.env` automatically.** Export its values into your terminal before running Django:

```bash
set -a
source .env
set +a
```

Repeat this in each new terminal used for server, migration, or test commands. `.env` is ignored by Git. Although a `db.sqlite3` file may exist locally, the configured database backend is MySQL.

### 5. Apply migrations and create an administrator

```bash
uv run python manage.py migrate
uv run python manage.py createsuperuser
```

Follow the prompts for the admin username, email, and password. The superuser is useful for the admin interface and can also log in through the token API. A new database contains no menu items or bookings; create them through the admin interface or the examples below.

### 6. Start the development server

```bash
uv run python manage.py check
uv run python manage.py runserver
```

Open:

- Homepage: http://127.0.0.1:8000/restaurant/
- Menu API: http://127.0.0.1:8000/restaurant/menu/
- Admin: http://127.0.0.1:8000/admin/

An empty menu returns `[]`. The bare URL `http://127.0.0.1:8000/` has no route and returns 404. Stop the server with `Ctrl+C`.

To use another port, run `uv run python manage.py runserver 8001` and adjust the URLs accordingly. The checked-in settings use `DEBUG=True` and a development secret key; they are intended for local development.

### 7. Register, log in, and make a booking

Keep the server running and use a second terminal for these requests. You may skip registration if you want to log in with your superuser credentials.

Register a user (choose your own password):

```bash
curl -X POST http://127.0.0.1:8000/auth/users/ \
  -H 'Content-Type: application/json' \
  -d '{"username":"demo","email":"demo@example.com","password":"LemonTable!4826"}'
```

Log in with the same credentials:

```bash
curl -X POST http://127.0.0.1:8000/auth/token/login/ \
  -H 'Content-Type: application/json' \
  -d '{"username":"demo","password":"LemonTable!4826"}'
```

The response contains `{"auth_token":"..."}`. Copy that value:

```bash
export TOKEN='paste-your-auth_token-here'
```

Create and list bookings:

```bash
curl -X POST http://127.0.0.1:8000/restaurant/booking/tables/ \
  -H "Authorization: Token $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"name":"Demo Guest","number_of_guests":4,"booking_date":"2026-12-15"}'

curl http://127.0.0.1:8000/restaurant/booking/tables/ \
  -H "Authorization: Token $TOKEN"
```

Create and list menu items:

```bash
curl -X POST http://127.0.0.1:8000/restaurant/menu/ \
  -H 'Content-Type: application/json' \
  -d '{"title":"Pasta","price":"12.99","inventory":10}'

curl http://127.0.0.1:8000/restaurant/menu/
```

## Endpoint reference

All paths below are relative to `http://127.0.0.1:8000`. Use the trailing slashes shown. Send JSON bodies with `Content-Type: application/json`. Replace `<id>` with the record's actual ID.

Authenticated API requests use `Authorization: Token <token>` (not `Bearer`). Django session authentication is also enabled; session-authenticated writes require a CSRF token. API views support `OPTIONS`, and views with `GET` also support `HEAD`. Router-generated user and booking URLs additionally accept format suffixes such as `/auth/users.json` and `/restaurant/booking/tables.json`.

### Restaurant and booking endpoints

| Method | Path | Authentication | Description |
| --- | --- | --- | --- |
| GET | `/restaurant/` | Public | Render the restaurant homepage. |
| GET | `/restaurant/menu/` | Public | List all menu items. |
| POST | `/restaurant/menu/` | Public | Create a menu item. |
| GET | `/restaurant/menu/<id>/` | Public | Retrieve a menu item. |
| PUT, PATCH | `/restaurant/menu/<id>/` | Public | Replace or partially update a menu item. |
| DELETE | `/restaurant/menu/<id>/` | Public | Delete a menu item. |
| GET | `/restaurant/booking/` | Public | Booking API root with a link to the tables endpoint. |
| GET | `/restaurant/booking/tables/` | Required | List all bookings. |
| POST | `/restaurant/booking/tables/` | Required | Create a booking. |
| GET | `/restaurant/booking/tables/<id>/` | Required | Retrieve a booking. |
| PUT, PATCH | `/restaurant/booking/tables/<id>/` | Required | Replace or partially update a booking. |
| DELETE | `/restaurant/booking/tables/<id>/` | Required | Delete a booking. |

Menu writes are public under the current permissions. Any authenticated user can read and modify any booking; bookings are not associated with an owning account.

Menu request fields:

| Field | Type | Notes |
| --- | --- | --- |
| `title` | String | Required; maximum 255 characters. |
| `price` | Decimal | Required; up to 10 digits total and 2 decimal places, e.g. `"12.99"`. |
| `inventory` | Integer | Required. |

Booking request fields:

| Field | Type | Notes |
| --- | --- | --- |
| `name` | String | Required; maximum 255 characters. |
| `number_of_guests` | Integer | Required. |
| `booking_date` | Date | Required; `YYYY-MM-DD`. |

Both resources return a generated, read-only `id`. Send all required fields for `POST` and `PUT`; send only changed fields for `PATCH`. Successful creates return 201, reads/updates return 200, and deletes return 204. Validation errors return 400; missing records return 404. Lists are not paginated in the current configuration.

### Login and token endpoints

| Method | Path | Authentication | Body / behavior |
| --- | --- | --- | --- |
| POST | `/auth/token/login/` | Public | `username`, `password`; returns `auth_token`. |
| POST | `/restaurant/api-token-auth/` | Public | `username`, `password`; returns `token`. Alternative token login endpoint. |
| POST | `/auth/token/logout/` | Required | No body needed; invalidates the user's token and returns 204. |

Both login endpoints use the same DRF token system; only their response key names differ.

```bash
curl -X POST http://127.0.0.1:8000/auth/token/logout/ \
  -H "Authorization: Token $TOKEN"
```

### User account endpoints (Djoser)

| Method | Path | Authentication | Body / behavior |
| --- | --- | --- | --- |
| GET | `/auth/` | Public | User API root. |
| POST | `/auth/users/` | Public | Register with `username`, `password`, and optional `email`. |
| GET | `/auth/users/` | Required | Regular users see their own account; staff can list all users. |
| GET | `/auth/users/me/` | Required | Retrieve the current account. |
| PUT, PATCH | `/auth/users/me/` | Required | Update the current account's `email`. |
| DELETE | `/auth/users/me/` | Required | Delete the current account; send `current_password`. |
| GET | `/auth/users/<id>/` | Owner or staff | Retrieve an account. |
| PUT, PATCH | `/auth/users/<id>/` | Owner or staff | Update an account's `email`. |
| DELETE | `/auth/users/<id>/` | Owner or staff | Delete an account; send the requesting user's `current_password`. |
| POST | `/auth/users/set_password/` | Required | `current_password`, `new_password`. |
| POST | `/auth/users/set_username/` | Required | `current_password`, `new_username`. |
| POST | `/auth/users/reset_password/` | Public | `email`; request a password reset email.* |
| POST | `/auth/users/reset_password_confirm/` | Public | `uid`, `token`, `new_password`; confirm a reset.* |
| POST | `/auth/users/reset_username/` | Public | `email`; request a username reset email.* |
| POST | `/auth/users/reset_username_confirm/` | Public | `uid`, `token`, `new_username`; confirm a reset.* |
| POST | `/auth/users/activation/` | Public | `uid`, `token`; activate an account.* |
| POST | `/auth/users/resend_activation/` | Public | `email`; resend activation email.* |

Account responses expose `id`, `username`, and `email`. Change usernames and passwords through the dedicated actions above, rather than profile updates. Passwords must pass Django's configured password validators.

\* These routes are registered, but the project does not configure an email delivery service or Djoser reset/activation URL templates. Email-based flows need an email backend plus the relevant `DJOSER` settings (`PASSWORD_RESET_CONFIRM_URL`, `USERNAME_RESET_CONFIRM_URL`, and, for activation, `ACTIVATION_URL` and `SEND_ACTIVATION_EMAIL`). New accounts are active immediately with the current defaults; resending activation returns 400 while activation emails are disabled. Reset confirmation requires a valid `uid` and reset token, which is different from an API login token.

### Admin and static files

The Django admin uses session login with an active staff account; model operations also require the appropriate permissions. A superuser has all permissions. These are HTML pages, not JSON API endpoints.

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/admin/` | Admin dashboard. |
| GET, POST | `/admin/login/` | Admin login form and submission. |
| POST | `/admin/logout/` | Log out of the admin session. |
| GET, POST | `/admin/password_change/` | Change the logged-in user's password. |
| GET | `/admin/password_change/done/` | Password change confirmation. |
| GET | `/admin/<app>/` | App index (`auth`, `restaurant`, or `authtoken`). |
| GET | `/admin/<app>/<model>/` | Model list. |
| GET, POST | `/admin/<app>/<model>/add/` | Create a record. |
| GET, POST | `/admin/<app>/<model>/<id>/change/` | View/edit a record. |
| GET, POST | `/admin/<app>/<model>/<id>/delete/` | Confirm/delete a record. |
| GET | `/admin/<app>/<model>/<id>/history/` | Record change history. |
| GET | `/admin/<app>/<model>/<id>/` | Redirect to the record's change page. |
| GET, POST | `/admin/auth/user/<id>/password/` | Change a user's password. |
| GET | `/admin/autocomplete/` | Admin autocomplete helper. |
| GET | `/admin/jsi18n/` | Admin JavaScript translations. |
| GET | `/admin/r/<content_type_id>/<object_id>/` | Admin “view on site” redirect, where supported by a model. |
| GET | `/static/<path>` | Development static assets, served by `runserver`. |

Registered app/model pairs are `restaurant/menu`, `restaurant/booking`, `auth/user`, `auth/group`, and `authtoken/tokenproxy`. Static restaurant assets are under `/static/restaurant/`.

## Run the tests

The suite covers model string representations and the menu list endpoint. Django creates a separate `test_littlelemon` database by default. As a MySQL administrator, grant the local application user permission to create and remove that test database:

```sql
GRANT ALL PRIVILEGES ON test_littlelemon.* TO 'littlelemon'@'127.0.0.1';
```

If you changed `MYSQL_DATABASE`, use `test_<your_database_name>` instead. From a terminal with your database environment variables loaded, run:

```bash
uv run python manage.py test tests
```

To run only the view tests:

```bash
uv run python manage.py test tests.test_views
```

## Troubleshooting

| Problem | What to check |
| --- | --- |
| `mysqlclient` fails to install | Install the native MySQL development libraries, `pkg-config`, compiler tools, and matching Python headers; then rerun `uv sync --locked`. On macOS, install Xcode command-line tools with `xcode-select --install` if needed. |
| Cannot connect to MySQL | Start MySQL and check `MYSQL_HOST` and `MYSQL_PORT`. |
| Access denied for MySQL user | Check the username/password, the user's host (`127.0.0.1` in this guide), grants, and that `.env` has been exported in this terminal. |
| Unknown database or missing tables | Create the database, then run `uv run python manage.py migrate`. |
| Booking request returns 401 | Send `Authorization: Token <token>` using a valid login token. |
| Session-authenticated write returns 403 | Include the session's CSRF token, or use token authentication as shown above. |
| `/` returns 404 | Open `/restaurant/` for the homepage. |
| Tests cannot create their database | Grant privileges on the separate `test_<database_name>` database. |
| Port 8000 is in use | Run `uv run python manage.py runserver 8001`. |

## Project layout

- `littlelemon/settings.py`: Django, database, and authentication configuration.
- `littlelemon/urls.py`: Admin, Djoser, and booking router URLs.
- `restaurant/`: Menu and booking models, serializers, views, migrations, and static assets.
- `restaurant/urls.py`: Homepage, menu, and alternative token login URLs.
- `templates/index.html`: Restaurant homepage template.
- `tests/`: Model and menu API tests.
- `pyproject.toml` / `uv.lock`: Python requirements and locked dependencies.
