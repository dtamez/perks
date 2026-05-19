# Perks

A benefits enrollment platform built with Flask and PostgreSQL.

---

## Overview

Perks simulates a benefits enrollment system with:

- Relational data modeling
- User enrollment workflows
- Administrative configuration
- Clear separation of application layers

---

## Architecture

**Application Structure**

- Flask application using SQLAlchemy ORM  
- PostgreSQL relational schema  
- Migration-based schema management  
- REST-style route design  
- Separation of service logic and persistence  
- Test coverage for core workflows  

---

## Tech Stack

Python · Flask · SQLAlchemy · PostgreSQL

---

## Running Locally

```bash
git clone https://github.com/dtamez/perks
cd perks

python -m venv venv
source venv/bin/activate

pip install -r requirements.txt

# If using Flask-Migrate / Alembic:
flask db upgrade

flask run
