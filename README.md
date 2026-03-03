---

# 📘 `perks` README.md

```markdown
# Perks

A benefits enrollment platform built with Flask and PostgreSQL.

This project models relational business workflows and demonstrates clean RESTful backend architecture.

---

## Overview

Perks simulates a benefits enrollment system with:

- Relational data modeling
- User enrollment workflows
- Administrative configuration
- Clean separation of application layers

The goal was to build a realistic backend service emphasizing maintainable structure and clear domain modeling.

---

## Architecture Notes

- Flask application using SQLAlchemy ORM
- PostgreSQL relational schema
- Migration-based schema management
- RESTful route design
- Separation of service logic and persistence
- Test coverage for core workflows

This project focuses on backend correctness and clarity over UI complexity.

---

## Tech Stack

- Python
- Flask
- SQLAlchemy
- PostgreSQL

---

## Running Locally

```bash
git clone https://github.com/dtamez/perks
cd perks
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
flask db upgrade
flask run

