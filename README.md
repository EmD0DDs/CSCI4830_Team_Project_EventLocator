# CSCI4830_Team_Project_EventLocator

This project is an event locator for users to view events that are happening in Omaha.

## Local setup

### 1. Requirements

- Python 3.14
- PostgreSQL 17
- Git

On Mac, install PostgreSQL with Homebrew:

```bash
brew install postgresql@17
```

Homebrew doesn't add `psql` to your PATH for this version, so add it once and restart the terminal:

```bash
echo 'export PATH="/opt/homebrew/opt/postgresql@17/bin:$PATH"' >> ~/.zshrc
```

On Windows, use the installer from https://www.postgresql.org/download/windows/ and remember the password you set for the `postgres` user.

### 2. Clone the repo

```bash
git clone https://github.com/EmD0DDs/CSCI4830_Team_Project_EventLocator.git
cd CSCI4830_Team_Project_EventLocator
```

### 3. Create the database

Start PostgreSQL (Mac):

```bash
brew services start postgresql@17
```

Open psql as an admin user. On Mac:

```bash
psql postgres
```

On Windows:

```bash
psql -U postgres
```

Then create the user and database. Pick your own password and replace `your_password_here`:

```sql
CREATE ROLE eventlocator WITH LOGIN CREATEDB PASSWORD 'your_password_here';
CREATE DATABASE eventlocator OWNER eventlocator;
\q
```

`CREATEDB` is needed because `python manage.py test` creates a temporary test database.

### 4. Virtual environment and packages

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On Windows, activate with `.venv\Scripts\activate` instead.

Check that the right environment is active. The path should end in `CSCI4830_Team_Project_EventLocator/.venv/bin/python`:

```bash
which python
```

### 5. Environment variables

```bash
cp .env.example .env
```

Open `.env` and set `DB_PASSWORD` to the password from step 3. The other values work as they are.

Never commit `.env`. It's already in `.gitignore`.

### 6. Run it

```bash
python manage.py migrate
python manage.py runserver
```

Then open http://127.0.0.1:8000/

Run the tests with:

```bash
python manage.py test
```

### Troubleshooting

| Error | Fix |
|---|---|
| `ModuleNotFoundError: No module named 'dotenv'` (or `django`, `psycopg`) | Wrong or no virtual environment. Run `deactivate`, then `source .venv/bin/activate`, and check `which python` |
| `KeyError: 'DB_NAME'` | `.env` is missing or a name is misspelled. Compare it with `.env.example` |
| `connection refused` | PostgreSQL isn't running. Run `brew services start postgresql@17` |
| `password authentication failed for user "eventlocator"` | The password in `.env` doesn't match the one from step 3 |
| `permission denied for schema public` | The database isn't owned by `eventlocator`. In `psql postgres`, run `ALTER DATABASE eventlocator OWNER TO eventlocator;` |
| `permission denied to create database` (during tests) | In `psql postgres`, run `ALTER ROLE eventlocator CREATEDB;` |
