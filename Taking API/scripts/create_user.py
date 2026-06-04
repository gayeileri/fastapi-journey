#!/usr/bin/env python3
"""Create a user with a hashed password for local testing.
Usage: python scripts/create_user.py username password

Requires the database to be reachable (settings.DATABASE_URL).
"""
import sys
from sqlalchemy.exc import IntegrityError
from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash


def main():
    if len(sys.argv) < 3:
        print("Usage: python scripts/create_user.py <username> <password>")
        sys.exit(1)
    username = sys.argv[1]
    password = sys.argv[2]

    db = SessionLocal()
    try:
        hashed = get_password_hash(password)
        user = User(username=username, password_hash=hashed)
        db.add(user)
        db.commit()
        print(f"Created user '{username}'")
    except IntegrityError:
        db.rollback()
        print(f"User '{username}' already exists")
    finally:
        db.close()


if __name__ == '__main__':
    main()
